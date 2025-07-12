"""
Enhanced Communication Features for Merrywinter Security Consulting
Secure messaging, alerts, and communication management - SLASH COMMANDS ONLY
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random
import asyncio

from config.settings import Config
from utils.helpers import get_user_clearance, create_embed
from utils.storage import Storage

class CommunicationSystem(commands.Cog):
    """Enhanced communication and alert system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage = Storage()
        self.active_alerts = {}
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if interaction is in authorized guild"""
        return Config.check_guild_authorization(interaction.guild.id)
    
    @app_commands.command(name="secure_message", description="Send secure encrypted message (BETA+ clearance)")
    @app_commands.describe(
        recipient="User to send secure message to (optional if using role_target)",
        message="Secure message content",
        classification="Classification level of message",
        auto_delete="Auto-delete message after specified minutes",
        role_target="Send to all users with this role (optional)"
    )
    @app_commands.choices(
        classification=[
            app_commands.Choice(name="Confidential", value="confidential"),
            app_commands.Choice(name="Secret", value="secret"),
            app_commands.Choice(name="Top Secret", value="top_secret")
        ],
        auto_delete=[
            app_commands.Choice(name="5 minutes", value=5),
            app_commands.Choice(name="15 minutes", value=15),
            app_commands.Choice(name="30 minutes", value=30),
            app_commands.Choice(name="1 hour", value=60),
            app_commands.Choice(name="No auto-delete", value=0)
        ]
    )
    async def secure_message(self, interaction: discord.Interaction, message: str, classification: str = "confidential", auto_delete: int = 0, recipient: discord.Member = None, role_target: discord.Role = None):
        """Send secure encrypted message"""
        user_roles = [role.name for role in interaction.user.roles]
        
        # Check if user has Executive Command or Command Level+ clearance (officers only)
        allowed_roles = ["Executive Command", "Director of Intelligence and Security"]
        has_executive_access = any(role in user_roles for role in allowed_roles)
        user_clearance = get_user_clearance(interaction.user.roles)
        has_officer_access = Config.has_permission(user_clearance, 'COMMAND_LEVEL')
        
        if not (has_executive_access or has_officer_access):
            await interaction.response.send_message("❌ You need Executive Command role or Command Level+ clearance to send secure messages.", ephemeral=True)
            return
        
        # Check if either recipient or role_target is provided
        if not recipient and not role_target:
            await interaction.response.send_message("❌ You must specify either a recipient or a role target.", ephemeral=True)
            return
        
        # Check classification access for sender
        classification_requirements = {
            'confidential': 'COMMAND_LEVEL',  # Officers can send confidential
            'secret': 'EXECUTIVE_COMMAND',  # Only Executive Command can send secret messages
            'top_secret': 'EXECUTIVE_COMMAND'
        }
        
        required_clearance = classification_requirements.get(classification, 'BETA')
        
        # Check if user has required clearance for this classification
        if classification == 'secret' or classification == 'top_secret':
            # Only Executive Command can send secret/top secret messages
            if not has_executive_access:
                await interaction.response.send_message(f"❌ Only Executive Command can send {classification.replace('_', ' ').title()} messages.", ephemeral=True)
                return
        else:
            # For confidential messages, check normal clearance
            if not has_executive_access:
                if not Config.has_permission(user_clearance, required_clearance):
                    await interaction.response.send_message(f"❌ You need {required_clearance.replace('_', ' ').title()} clearance to send {classification.replace('_', ' ').title()} messages.", ephemeral=True)
                    return
        
        # Generate message ID
        message_id = f"SECURE-{random.randint(100000, 999999)}"
        
        # Create classification colors
        classification_colors = {
            'confidential': 0x0066CC,
            'secret': 0xFF6600,
            'top_secret': 0xFF0000
        }
        
        # Determine recipients
        recipients = []
        if recipient:
            recipients.append(recipient)
        
        if role_target:
            # Get all members with the specified role
            role_members = [member for member in interaction.guild.members if role_target in member.roles and not member.bot]
            recipients.extend(role_members)
        
        # Remove duplicates
        recipients = list(set(recipients))
        
        if not recipients:
            await interaction.response.send_message("❌ No valid recipients found.", ephemeral=True)
            return
        
        # Send encrypted-style message to all recipients
        for target in recipients:
            await self._send_encrypted_message(target, {
                'message_id': message_id,
                'sender': interaction.user.display_name,
                'sender_clearance': user_clearance,
                'classification': classification,
                'content': message,
                'auto_delete': auto_delete,
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Save secure message data
        secure_data = {
            'message_id': message_id,
            'sender': interaction.user.id,
            'recipients': [r.id for r in recipients],
            'role_target': role_target.name if role_target else None,
            'classification': classification,
            'content': message,
            'auto_delete': auto_delete,
            'timestamp': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id
        }
        
        await self.storage.save_secure_message(secure_data)
        
        # Confirm to sender
        if role_target:
            await interaction.response.send_message(f"✅ Secure message `{message_id}` sent to {len(recipients)} members with role {role_target.name}", ephemeral=True)
        else:
            await interaction.response.send_message(f"✅ Secure message `{message_id}` sent to {recipient.display_name}", ephemeral=True)
    
    async def _send_encrypted_message(self, recipient: discord.Member, data: dict):
        """Send encrypted-style message with animation"""
        try:
            # Phase 1: Encryption notification
            encryption_embed = discord.Embed(
                title="🔐 ENCRYPTED MESSAGE INCOMING",
                description="```\n[████████████████████████████████] 100%\nENCRYPTION PROTOCOL: AES-256\nCLEARANCE VERIFICATION: IN PROGRESS...\n```",
                color=0x00FF00
            )
            
            dm_message = await recipient.send(embed=encryption_embed)
            await asyncio.sleep(2)
            
            # Phase 2: Decryption process
            decryption_embed = discord.Embed(
                title="🔓 DE-CRYPTING MESSAGE...",
                description="```\n[████████████████████████████████] 100%\nDECRYPTION PROTOCOL: ACTIVE\nCLEARANCE VERIFIED: AUTHORIZED\nMESSAGE DECRYPTED: SUCCESS\n```",
                color=0xFFFF00
            )
            
            await dm_message.edit(embed=decryption_embed)
            await asyncio.sleep(2)
            
            # Phase 3: Actual message content
            classification_colors = {
                'confidential': 0x0066CC,
                'secret': 0xFF6600,
                'top_secret': 0xFF0000
            }
            
            classification_display = {
                'confidential': "🔵 CONFIDENTIAL",
                'secret': "🟡 SECRET",
                'top_secret': "🔴 TOP SECRET"
            }
            
            final_embed = discord.Embed(
                title=f"📨 SECURE MESSAGE - {classification_display.get(data['classification'], 'CONFIDENTIAL')}",
                description=f"**Message ID:** {data['message_id']}\n"
                           f"**From:** {data['sender']} ({data['sender_clearance']})\n"
                           f"**Classification:** {data['classification'].replace('_', ' ').title()}\n"
                           f"**Timestamp:** {data['timestamp']} UTC",
                color=classification_colors.get(data['classification'], 0x0066CC)
            )
            
            final_embed.add_field(
                name="📄 Message Content",
                value=data['content'],
                inline=False
            )
            
            if data['auto_delete'] > 0:
                final_embed.add_field(
                    name="⏰ Auto-Delete",
                    value=f"This message will auto-delete in {data['auto_delete']} minutes",
                    inline=False
                )
            
            final_embed.set_footer(text=f"{Config.COMPANY_NAME} - Secure Communications")
            
            await dm_message.edit(embed=final_embed)
            
            # Schedule auto-delete if enabled
            if data['auto_delete'] > 0:
                await asyncio.sleep(data['auto_delete'] * 60)
                try:
                    await dm_message.delete()
                except:
                    pass
            
        except discord.Forbidden:
            pass  # User has DMs disabled
        except Exception as e:
            print(f"Error sending encrypted message: {e}")
    
    @app_commands.command(name="emergency_alert", description="Send emergency alert (Director+ clearance)")
    @app_commands.describe(
        alert_type="Type of emergency alert",
        severity="Severity level of the alert",
        message="Emergency alert message",
        duration="Alert duration in minutes"
    )
    @app_commands.choices(
        alert_type=[
            app_commands.Choice(name="Security Breach", value="security_breach"),
            app_commands.Choice(name="Hostile Activity", value="hostile_activity"),
            app_commands.Choice(name="Equipment Failure", value="equipment_failure"),
            app_commands.Choice(name="Personnel Emergency", value="personnel_emergency"),
            app_commands.Choice(name="Communication Failure", value="communication_failure"),
            app_commands.Choice(name="General Emergency", value="general_emergency")
        ],
        severity=[
            app_commands.Choice(name="Critical", value="critical"),
            app_commands.Choice(name="High", value="high"),
            app_commands.Choice(name="Medium", value="medium"),
            app_commands.Choice(name="Low", value="low")
        ],
        duration=[
            app_commands.Choice(name="5 minutes", value=5),
            app_commands.Choice(name="15 minutes", value=15),
            app_commands.Choice(name="30 minutes", value=30),
            app_commands.Choice(name="1 hour", value=60),
            app_commands.Choice(name="Until cancelled", value=0)
        ]
    )
    async def emergency_alert(self, interaction: discord.Interaction, alert_type: str, severity: str, message: str, duration: int = 15):
        """Send emergency alert"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        # Check if user has Command Level+ clearance (officers only)
        if not Config.has_permission(user_clearance, 'COMMAND_LEVEL'):
            await interaction.response.send_message("❌ You need Command Level+ clearance to send emergency alerts.", ephemeral=True)
            return
        
        # Generate alert ID
        alert_id = f"ALERT-{random.randint(100000, 999999)}"
        
        # Create severity colors
        severity_colors = {
            'critical': 0xFF0000,
            'high': 0xFF6600,
            'medium': 0xFFFF00,
            'low': 0x00FF00
        }
        
        # Create alert type icons
        alert_icons = {
            'security_breach': '🚨',
            'hostile_activity': '⚔️',
            'equipment_failure': '⚠️',
            'personnel_emergency': '🚑',
            'communication_failure': '📡',
            'general_emergency': '🔔'
        }
        
        # Create emergency alert embed
        embed = discord.Embed(
            title=f"{alert_icons.get(alert_type, '🔔')} EMERGENCY ALERT - {severity.upper()}",
            description=f"**Alert ID:** {alert_id}\n"
                       f"**Type:** {alert_type.replace('_', ' ').title()}\n"
                       f"**Severity:** {severity.upper()}\n"
                       f"**Issued By:** {interaction.user.display_name} ({user_clearance})\n"
                       f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            color=severity_colors.get(severity, 0xFFFF00)
        )
        
        embed.add_field(
            name="📢 Alert Message",
            value=message,
            inline=False
        )
        
        embed.add_field(
            name="⏰ Alert Duration",
            value=f"{duration} minutes" if duration > 0 else "Until cancelled",
            inline=True
        )
        
        embed.add_field(
            name="📋 Required Actions",
            value="• Acknowledge receipt of alert\n• Follow emergency protocols\n• Report to designated stations\n• Await further instructions",
            inline=False
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Emergency Alert System")
        
        # Send alert to all members with appropriate clearance
        await self._broadcast_emergency_alert(interaction.guild, embed, alert_type, severity)
        
        # Save alert data
        alert_data = {
            'alert_id': alert_id,
            'type': alert_type,
            'severity': severity,
            'message': message,
            'duration': duration,
            'issued_by': interaction.user.id,
            'timestamp': datetime.utcnow().isoformat(),
            'guild_id': interaction.guild.id,
            'active': True
        }
        
        await self.storage.save_emergency_alert(alert_data)
        
        # Store active alert
        self.active_alerts[alert_id] = alert_data
        
        # Schedule alert cancellation if duration is set
        if duration > 0:
            await asyncio.sleep(duration * 60)
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
        
        await interaction.response.send_message(f"🚨 Emergency alert `{alert_id}` has been broadcast!", ephemeral=True)
    
    async def _broadcast_emergency_alert(self, guild: discord.Guild, embed: discord.Embed, alert_type: str, severity: str):
        """Broadcast emergency alert to appropriate members"""
        # Get members with appropriate clearance (officers and senior enlisted)
        clearance_levels = ['EXECUTIVE_COMMAND', 'DEPARTMENT_DIRECTORS', 'COMMAND_LEVEL', 'SPECIALIZED_UNITS', 'OMEGA']
        
        for member in guild.members:
            if member.bot:
                continue
                
            member_clearance = get_user_clearance(member.roles)
            
            # Send to members with appropriate clearance
            if any(Config.has_permission(member_clearance, level) for level in clearance_levels):
                try:
                    await member.send(embed=embed)
                    await asyncio.sleep(0.5)  # Rate limiting
                except discord.Forbidden:
                    pass  # User has DMs disabled
                except Exception as e:
                    print(f"Error sending alert to {member.display_name}: {e}")
    
    @app_commands.command(name="cancel_alert", description="Cancel active emergency alert (Director+ clearance)")
    @app_commands.describe(
        alert_id="Alert ID to cancel"
    )
    async def cancel_alert(self, interaction: discord.Interaction, alert_id: str):
        """Cancel active emergency alert"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        # Check if user has Command Level+ clearance (officers only)
        if not Config.has_permission(user_clearance, 'COMMAND_LEVEL'):
            await interaction.response.send_message("❌ You need Command Level+ clearance to cancel emergency alerts.", ephemeral=True)
            return
        
        # Check if alert exists and is active
        if alert_id not in self.active_alerts:
            await interaction.response.send_message("❌ Alert not found or already cancelled.", ephemeral=True)
            return
        
        # Cancel the alert
        alert_data = self.active_alerts[alert_id]
        del self.active_alerts[alert_id]
        
        # Create cancellation embed
        embed = discord.Embed(
            title="✅ EMERGENCY ALERT CANCELLED",
            description=f"**Alert ID:** {alert_id}\n"
                       f"**Type:** {alert_data['type'].replace('_', ' ').title()}\n"
                       f"**Cancelled By:** {interaction.user.display_name} ({user_clearance})\n"
                       f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            color=0x00FF00
        )
        
        embed.add_field(
            name="📢 Cancellation Notice",
            value="Emergency alert has been cancelled. Resume normal operations.",
            inline=False
        )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Emergency Alert System")
        
        # Broadcast cancellation
        await self._broadcast_emergency_alert(interaction.guild, embed, "alert_cancelled", "info")
        
        await interaction.response.send_message(f"✅ Emergency alert `{alert_id}` has been cancelled!", ephemeral=True)
    
    @app_commands.command(name="status_report", description="Generate automated status report (Chief+ clearance)")
    @app_commands.describe(
        report_type="Type of status report to generate"
    )
    @app_commands.choices(
        report_type=[
            app_commands.Choice(name="Personnel Status", value="personnel"),
            app_commands.Choice(name="Operations Status", value="operations"),
            app_commands.Choice(name="Security Status", value="security"),
            app_commands.Choice(name="Communications Status", value="communications"),
            app_commands.Choice(name="Overall Status", value="overall")
        ]
    )
    async def status_report(self, interaction: discord.Interaction, report_type: str):
        """Generate automated status report"""
        user_clearance = get_user_clearance(interaction.user.roles)
        
        # Check if user has Command Level+ clearance (officers only)
        if not Config.has_permission(user_clearance, 'COMMAND_LEVEL'):
            await interaction.response.send_message("❌ You need Command Level+ clearance to generate status reports.", ephemeral=True)
            return
        
        # Generate report content
        report_content = self._generate_status_report(report_type, interaction.guild)
        
        # Create status report embed
        embed = discord.Embed(
            title=f"📊 STATUS REPORT - {report_content['title']}",
            description=f"**Report Type:** {report_type.replace('_', ' ').title()}\n"
                       f"**Generated By:** {interaction.user.display_name}\n"
                       f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                       f"**Overall Status:** {report_content['overall_status']}",
            color=report_content['color']
        )
        
        for section in report_content['sections']:
            embed.add_field(
                name=section['name'],
                value=section['value'],
                inline=section.get('inline', False)
            )
        
        embed.set_footer(text=f"{Config.COMPANY_NAME} - Automated Status System")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _generate_status_report(self, report_type: str, guild: discord.Guild) -> dict:
        """Generate status report content"""
        
        # Get guild statistics
        total_members = len([m for m in guild.members if not m.bot])
        online_members = len([m for m in guild.members if not m.bot and m.status != discord.Status.offline])
        
        report_templates = {
            'personnel': {
                'title': 'PERSONNEL STATUS REPORT',
                'overall_status': random.choice(['OPERATIONAL', 'READY', 'STANDBY']),
                'color': 0x00FF00,
                'sections': [
                    {
                        'name': '👥 Personnel Statistics',
                        'value': f"**Total Personnel:** {total_members}\n**Online:** {online_members}\n**Offline:** {total_members - online_members}\n**Readiness:** {random.randint(85, 98)}%",
                        'inline': True
                    },
                    {
                        'name': '🎯 Deployment Status',
                        'value': f"**Available:** {random.randint(15, 25)}\n**Deployed:** {random.randint(8, 15)}\n**Training:** {random.randint(3, 8)}\n**Leave:** {random.randint(1, 5)}",
                        'inline': True
                    },
                    {
                        'name': '📋 Recent Activity',
                        'value': f"• {random.randint(2, 5)} personnel promoted\n• {random.randint(1, 3)} new assignments\n• {random.randint(0, 2)} personnel on medical leave\n• {random.randint(1, 4)} training completions",
                        'inline': False
                    }
                ]
            },
            'operations': {
                'title': 'OPERATIONS STATUS REPORT',
                'overall_status': random.choice(['ACTIVE', 'NOMINAL', 'READY']),
                'color': 0x0066CC,
                'sections': [
                    {
                        'name': '🎯 Active Operations',
                        'value': f"**Total Operations:** {random.randint(3, 8)}\n**In Progress:** {random.randint(2, 5)}\n**Completed:** {random.randint(5, 12)}\n**Success Rate:** {random.randint(92, 99)}%",
                        'inline': True
                    },
                    {
                        'name': '🚁 Deployments',
                        'value': f"**Active:** {random.randint(2, 6)}\n**Scheduled:** {random.randint(1, 4)}\n**Completed:** {random.randint(8, 15)}\n**Efficiency:** {random.randint(88, 96)}%",
                        'inline': True
                    },
                    {
                        'name': '📈 Performance Metrics',
                        'value': f"• Mission success rate: {random.randint(95, 99)}%\n• Average response time: {random.randint(8, 15)} minutes\n• Resource utilization: {random.randint(78, 89)}%\n• Equipment readiness: {random.randint(92, 98)}%",
                        'inline': False
                    }
                ]
            },
            'security': {
                'title': 'SECURITY STATUS REPORT',
                'overall_status': random.choice(['SECURE', 'PROTECTED', 'NOMINAL']),
                'color': 0xFF6600,
                'sections': [
                    {
                        'name': '🔒 Security Level',
                        'value': f"**Current Level:** {random.choice(['NORMAL', 'ELEVATED', 'HIGH'])}\n**Threat Level:** {random.choice(['LOW', 'MODERATE'])}\n**Incidents:** {random.randint(0, 2)}\n**Breaches:** 0",
                        'inline': True
                    },
                    {
                        'name': '🛡️ Defensive Status',
                        'value': f"**Perimeter:** SECURE\n**Access Control:** ACTIVE\n**Surveillance:** OPERATIONAL\n**Response:** {random.randint(95, 99)}%",
                        'inline': True
                    },
                    {
                        'name': '📊 Security Metrics',
                        'value': f"• Access attempts: {random.randint(45, 78)}\n• Authorized entries: {random.randint(42, 75)}\n• Unauthorized attempts: {random.randint(0, 3)}\n• System uptime: {random.randint(98, 100)}%",
                        'inline': False
                    }
                ]
            },
            'communications': {
                'title': 'COMMUNICATIONS STATUS REPORT',
                'overall_status': random.choice(['OPERATIONAL', 'ACTIVE', 'NOMINAL']),
                'color': 0x9932CC,
                'sections': [
                    {
                        'name': '📡 Communication Systems',
                        'value': f"**Primary:** OPERATIONAL\n**Secondary:** STANDBY\n**Encrypted:** ACTIVE\n**Uptime:** {random.randint(98, 100)}%",
                        'inline': True
                    },
                    {
                        'name': '📊 Traffic Analysis',
                        'value': f"**Messages:** {random.randint(156, 234)}\n**Secure:** {random.randint(23, 45)}\n**Alerts:** {random.randint(2, 8)}\n**Bandwidth:** {random.randint(67, 89)}%",
                        'inline': True
                    },
                    {
                        'name': '🔐 Security Status',
                        'value': f"• Encryption: AES-256 Active\n• Authentication: Multi-factor\n• Intrusion detection: Active\n• Communication security: {random.randint(96, 100)}%",
                        'inline': False
                    }
                ]
            },
            'overall': {
                'title': 'OVERALL STATUS REPORT',
                'overall_status': random.choice(['OPERATIONAL', 'READY', 'NOMINAL']),
                'color': 0x00FF00,
                'sections': [
                    {
                        'name': '📊 System Overview',
                        'value': f"**Personnel:** {random.randint(88, 96)}%\n**Operations:** {random.randint(92, 98)}%\n**Security:** {random.randint(95, 100)}%\n**Communications:** {random.randint(87, 95)}%",
                        'inline': True
                    },
                    {
                        'name': '🎯 Readiness Level',
                        'value': f"**Combat:** {random.randint(90, 98)}%\n**Support:** {random.randint(85, 95)}%\n**Logistics:** {random.randint(78, 88)}%\n**Intelligence:** {random.randint(82, 92)}%",
                        'inline': True
                    },
                    {
                        'name': '📈 Performance Summary',
                        'value': f"• Overall efficiency: {random.randint(89, 96)}%\n• Mission readiness: {random.randint(92, 99)}%\n• Resource availability: {random.randint(84, 93)}%\n• System reliability: {random.randint(95, 100)}%",
                        'inline': False
                    }
                ]
            }
        }
        
        return report_templates.get(report_type, report_templates['overall'])

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(CommunicationSystem(bot))