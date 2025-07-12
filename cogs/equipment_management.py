"""
Equipment Checkout System for FROST AI
Track who has what gear/weapons in the PMC organization
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime, timedelta
from config.settings import Config
from utils.helpers import create_embed
from utils.storage import Storage

class EquipmentManagement(commands.Cog):
    """Equipment checkout and tracking system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        
    def cog_check(self, ctx):
        """Check if command is used in authorized guild"""
        return Config.check_guild_authorization(ctx.guild.id)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    @app_commands.command(name="equipment-add", description="Add equipment to inventory (Admin only)")
    @app_commands.describe(
        name="Equipment name",
        category="Equipment category (weapon, gear, vehicle, electronics)",
        description="Equipment description",
        serial_number="Serial number or identifier",
        condition="Equipment condition (excellent, good, fair, poor)"
    )
    async def add_equipment(
        self, 
        interaction: discord.Interaction,
        name: str,
        category: str,
        description: str = None,
        serial_number: str = None,
        condition: str = "good"
    ):
        """Add equipment to inventory"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message(
                "❌ Access denied. Moderator permissions required.",
                ephemeral=True
            )
            return
        
        # Load equipment data
        equipment_data = await self.storage.load_equipment_inventory()
        
        # Generate equipment ID
        equipment_id = f"EQ-{len(equipment_data) + 1:04d}"
        
        # Create equipment entry
        equipment_entry = {
            'id': equipment_id,
            'name': name,
            'category': category.lower(),
            'description': description or "No description provided",
            'serial_number': serial_number or "N/A",
            'condition': condition.lower(),
            'status': 'available',
            'checked_out_to': None,
            'checked_out_by': None,
            'checkout_date': None,
            'expected_return': None,
            'added_by': interaction.user.id,
            'added_date': datetime.utcnow().isoformat(),
            'checkout_history': []
        }
        
        equipment_data[equipment_id] = equipment_entry
        await self.storage.save_equipment_inventory(equipment_data)
        
        # Create response embed
        embed = create_embed(
            title="🛠️ Equipment Added to Inventory",
            description=f"**{name}** has been added to the equipment inventory",
            color=Config.COLORS['success']
        )
        
        embed.add_field(name="Equipment ID", value=f"`{equipment_id}`", inline=True)
        embed.add_field(name="Category", value=category.title(), inline=True)
        embed.add_field(name="Condition", value=condition.title(), inline=True)
        embed.add_field(name="Serial Number", value=serial_number or "N/A", inline=True)
        embed.add_field(name="Status", value="Available", inline=True)
        
        if description:
            embed.add_field(name="Description", value=description, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="equipment-checkout", description="Check out equipment to an operator")
    @app_commands.describe(
        equipment_id="Equipment ID to check out",
        operator="Operator to check out to",
        duration_days="Expected return in days (default: 7)",
        purpose="Purpose of checkout"
    )
    async def checkout_equipment(
        self,
        interaction: discord.Interaction,
        equipment_id: str,
        operator: discord.Member,
        duration_days: int = 7,
        purpose: str = "Operational use"
    ):
        """Check out equipment to an operator"""
        # Check permissions
        if not Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id):
            await interaction.response.send_message(
                "❌ Access denied. Moderator permissions required.",
                ephemeral=True
            )
            return
        
        # Load equipment data
        equipment_data = await self.storage.load_equipment_inventory()
        
        if equipment_id not in equipment_data:
            await interaction.response.send_message(
                f"❌ Equipment ID `{equipment_id}` not found in inventory.",
                ephemeral=True
            )
            return
        
        equipment = equipment_data[equipment_id]
        
        if equipment['status'] != 'available':
            await interaction.response.send_message(
                f"❌ Equipment `{equipment_id}` is currently {equipment['status']}.",
                ephemeral=True
            )
            return
        
        # Update equipment status
        checkout_date = datetime.utcnow()
        expected_return = checkout_date + timedelta(days=duration_days)
        
        equipment['status'] = 'checked_out'
        equipment['checked_out_to'] = operator.id
        equipment['checked_out_by'] = interaction.user.id
        equipment['checkout_date'] = checkout_date.isoformat()
        equipment['expected_return'] = expected_return.isoformat()
        
        # Add to checkout history
        equipment['checkout_history'].append({
            'operator_id': operator.id,
            'operator_name': operator.display_name,
            'checked_out_by': interaction.user.id,
            'checkout_date': checkout_date.isoformat(),
            'expected_return': expected_return.isoformat(),
            'purpose': purpose,
            'returned': False
        })
        
        await self.storage.save_equipment_inventory(equipment_data)
        
        # Create response embed
        embed = create_embed(
            title="📤 Equipment Checked Out",
            description=f"**{equipment['name']}** has been checked out",
            color=Config.COLORS['warning']
        )
        
        embed.add_field(name="Equipment", value=f"{equipment['name']} (`{equipment_id}`)", inline=True)
        embed.add_field(name="Operator", value=operator.mention, inline=True)
        embed.add_field(name="Duration", value=f"{duration_days} days", inline=True)
        embed.add_field(name="Expected Return", value=f"<t:{int(expected_return.timestamp())}:f>", inline=True)
        embed.add_field(name="Purpose", value=purpose, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="equipment-return", description="Return checked out equipment")
    @app_commands.describe(
        equipment_id="Equipment ID to return",
        condition="Equipment condition after use",
        notes="Return notes"
    )
    async def return_equipment(
        self,
        interaction: discord.Interaction,
        equipment_id: str,
        condition: str = "good",
        notes: str = None
    ):
        """Return checked out equipment"""
        # Load equipment data
        equipment_data = await self.storage.load_equipment_inventory()
        
        if equipment_id not in equipment_data:
            await interaction.response.send_message(
                f"❌ Equipment ID `{equipment_id}` not found in inventory.",
                ephemeral=True
            )
            return
        
        equipment = equipment_data[equipment_id]
        
        if equipment['status'] != 'checked_out':
            await interaction.response.send_message(
                f"❌ Equipment `{equipment_id}` is not currently checked out.",
                ephemeral=True
            )
            return
        
        # Check if user can return (either the person who checked it out or the operator)
        can_return = (
            interaction.user.id == equipment['checked_out_to'] or
            interaction.user.id == equipment['checked_out_by'] or
            Config.is_moderator([role.name for role in interaction.user.roles], interaction.user.id)
        )
        
        if not can_return:
            await interaction.response.send_message(
                "❌ You can only return equipment that was checked out to you or by you.",
                ephemeral=True
            )
            return
        
        # Update equipment status
        return_date = datetime.utcnow()
        checkout_date = datetime.fromisoformat(equipment['checkout_date'])
        days_out = (return_date - checkout_date).days
        
        # Update current checkout history entry
        for entry in equipment['checkout_history']:
            if not entry['returned'] and entry['operator_id'] == equipment['checked_out_to']:
                entry['returned'] = True
                entry['return_date'] = return_date.isoformat()
                entry['return_condition'] = condition
                entry['return_notes'] = notes
                entry['days_out'] = days_out
                break
        
        # Reset equipment status
        equipment['status'] = 'available'
        equipment['condition'] = condition.lower()
        equipment['checked_out_to'] = None
        equipment['checked_out_by'] = None
        equipment['checkout_date'] = None
        equipment['expected_return'] = None
        
        await self.storage.save_equipment_inventory(equipment_data)
        
        # Create response embed
        embed = create_embed(
            title="📥 Equipment Returned",
            description=f"**{equipment['name']}** has been returned",
            color=Config.COLORS['success']
        )
        
        embed.add_field(name="Equipment", value=f"{equipment['name']} (`{equipment_id}`)", inline=True)
        embed.add_field(name="Days Out", value=f"{days_out} days", inline=True)
        embed.add_field(name="Condition", value=condition.title(), inline=True)
        
        if notes:
            embed.add_field(name="Return Notes", value=notes, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="equipment-status", description="Check equipment status and availability")
    @app_commands.describe(
        equipment_id="Specific equipment ID (optional)",
        category="Filter by category (optional)",
        status="Filter by status (optional)"
    )
    async def equipment_status(
        self,
        interaction: discord.Interaction,
        equipment_id: str = None,
        category: str = None,
        status: str = None
    ):
        """Check equipment status"""
        equipment_data = await self.storage.load_equipment_inventory()
        
        if not equipment_data:
            await interaction.response.send_message(
                "📋 No equipment found in inventory.",
                ephemeral=True
            )
            return
        
        # If specific equipment ID requested
        if equipment_id:
            if equipment_id not in equipment_data:
                await interaction.response.send_message(
                    f"❌ Equipment ID `{equipment_id}` not found.",
                    ephemeral=True
                )
                return
            
            equipment = equipment_data[equipment_id]
            
            embed = create_embed(
                title=f"🛠️ Equipment Status - {equipment['name']}",
                description=f"Details for equipment `{equipment_id}`",
                color=Config.COLORS['info']
            )
            
            embed.add_field(name="Name", value=equipment['name'], inline=True)
            embed.add_field(name="Category", value=equipment['category'].title(), inline=True)
            embed.add_field(name="Condition", value=equipment['condition'].title(), inline=True)
            embed.add_field(name="Status", value=equipment['status'].title(), inline=True)
            embed.add_field(name="Serial Number", value=equipment['serial_number'], inline=True)
            
            if equipment['status'] == 'checked_out':
                operator = interaction.guild.get_member(equipment['checked_out_to'])
                embed.add_field(name="Checked Out To", value=operator.mention if operator else "Unknown", inline=True)
                embed.add_field(name="Expected Return", value=f"<t:{int(datetime.fromisoformat(equipment['expected_return']).timestamp())}:f>", inline=False)
            
            if equipment['description'] != "No description provided":
                embed.add_field(name="Description", value=equipment['description'], inline=False)
            
            await interaction.response.send_message(embed=embed)
            return
        
        # Filter equipment
        filtered_equipment = []
        for eq_id, eq_data in equipment_data.items():
            if category and eq_data['category'] != category.lower():
                continue
            if status and eq_data['status'] != status.lower():
                continue
            filtered_equipment.append((eq_id, eq_data))
        
        if not filtered_equipment:
            await interaction.response.send_message(
                "📋 No equipment matches the specified filters.",
                ephemeral=True
            )
            return
        
        # Create summary embed
        embed = create_embed(
            title="🛠️ Equipment Inventory Status",
            description="Current equipment status and availability",
            color=Config.COLORS['info']
        )
        
        # Count by status
        status_counts = {}
        category_counts = {}
        
        for eq_id, eq_data in filtered_equipment:
            status_counts[eq_data['status']] = status_counts.get(eq_data['status'], 0) + 1
            category_counts[eq_data['category']] = category_counts.get(eq_data['category'], 0) + 1
        
        # Add status summary
        status_text = ""
        for status, count in status_counts.items():
            status_text += f"**{status.title()}:** {count}\n"
        
        embed.add_field(name="Status Summary", value=status_text or "None", inline=True)
        
        # Add category summary
        category_text = ""
        for cat, count in category_counts.items():
            category_text += f"**{cat.title()}:** {count}\n"
        
        embed.add_field(name="Category Summary", value=category_text or "None", inline=True)
        embed.add_field(name="Total Items", value=str(len(filtered_equipment)), inline=True)
        
        # Show some equipment details
        equipment_list = ""
        for eq_id, eq_data in filtered_equipment[:10]:  # Show first 10
            status_icon = "🟢" if eq_data['status'] == 'available' else "🟡" if eq_data['status'] == 'checked_out' else "🔴"
            equipment_list += f"{status_icon} `{eq_id}` - {eq_data['name']} ({eq_data['category']})\n"
        
        if len(filtered_equipment) > 10:
            equipment_list += f"... and {len(filtered_equipment) - 10} more items"
        
        embed.add_field(name="Equipment List", value=equipment_list or "None", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="equipment-history", description="View equipment checkout history")
    @app_commands.describe(
        equipment_id="Equipment ID to view history for (optional)",
        operator="View history for specific operator (optional)"
    )
    async def equipment_history(
        self,
        interaction: discord.Interaction,
        equipment_id: str = None,
        operator: discord.Member = None
    ):
        """View equipment checkout history"""
        equipment_data = await self.storage.load_equipment_inventory()
        
        if not equipment_data:
            await interaction.response.send_message(
                "📋 No equipment found in inventory.",
                ephemeral=True
            )
            return
        
        history_entries = []
        
        # Collect history entries
        for eq_id, eq_data in equipment_data.items():
            if equipment_id and eq_id != equipment_id:
                continue
                
            for entry in eq_data['checkout_history']:
                if operator and entry['operator_id'] != operator.id:
                    continue
                
                entry['equipment_id'] = eq_id
                entry['equipment_name'] = eq_data['name']
                history_entries.append(entry)
        
        if not history_entries:
            await interaction.response.send_message(
                "📋 No checkout history found matching the criteria.",
                ephemeral=True
            )
            return
        
        # Sort by checkout date (most recent first)
        history_entries.sort(key=lambda x: x['checkout_date'], reverse=True)
        
        embed = create_embed(
            title="📋 Equipment Checkout History",
            description="Recent equipment checkout activity",
            color=Config.COLORS['info']
        )
        
        # Show recent entries
        history_text = ""
        for entry in history_entries[:10]:  # Show last 10 entries
            checkout_date = datetime.fromisoformat(entry['checkout_date'])
            status_icon = "✅" if entry['returned'] else "🟡"
            
            history_text += f"{status_icon} **{entry['equipment_name']}** (`{entry['equipment_id']}`)\n"
            history_text += f"   Operator: {entry['operator_name']}\n"
            history_text += f"   Date: <t:{int(checkout_date.timestamp())}:d>\n"
            
            if entry['returned']:
                return_date = datetime.fromisoformat(entry['return_date'])
                history_text += f"   Returned: <t:{int(return_date.timestamp())}:d>\n"
            else:
                expected_return = datetime.fromisoformat(entry['expected_return'])
                history_text += f"   Due: <t:{int(expected_return.timestamp())}:d>\n"
            
            history_text += "\n"
        
        embed.add_field(name="Recent Activity", value=history_text or "None", inline=False)
        
        if len(history_entries) > 10:
            embed.add_field(name="Note", value=f"Showing 10 of {len(history_entries)} total entries", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(EquipmentManagement(bot))