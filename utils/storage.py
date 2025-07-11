"""
Storage utilities for Merrywinter Security Consulting Bot
Handles JSON-based data persistence
"""

import json
import os
import aiofiles
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

class Storage:
    """Storage handler for bot data"""
    
    def __init__(self):
        self.data_dir = 'data'
        self.tickets_file = f'{self.data_dir}/tickets.json'
        self.operators_file = f'{self.data_dir}/operators.json'
        self.missions_file = f'{self.data_dir}/missions.json'
        self.warnings_file = f'{self.data_dir}/warnings.json'
        self.deployments_file = f'{self.data_dir}/deployments.json'
        self.operations_file = f'{self.data_dir}/operations.json'
        self.operation_logs_file = f'{self.data_dir}/operation_logs.json'
        
        self._ensure_data_directory()
        self._lock = asyncio.Lock()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def _load_json(self, file_path: str) -> Dict[str, Any]:
        """Load JSON data from file"""
        if not os.path.exists(file_path):
            return {}
        
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            return json.loads(content) if content else {}
    
    async def _save_json(self, file_path: str, data: Dict[str, Any]):
        """Save JSON data to file"""
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(data, indent=2))
    
    # Ticket Management
    async def save_ticket(self, ticket_data: Dict[str, Any]):
        """Save ticket data"""
        async with self._lock:
            tickets = await self._load_json(self.tickets_file)
            tickets[ticket_data['id']] = ticket_data
            await self._save_json(self.tickets_file, tickets)
    
    async def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket data by ID"""
        tickets = await self._load_json(self.tickets_file)
        return tickets.get(ticket_id)
    
    async def get_all_tickets(self) -> Dict[str, Any]:
        """Get all tickets"""
        return await self._load_json(self.tickets_file)
    
    # Warning Management
    async def save_warning(self, warning_data: Dict[str, Any]):
        """Save warning data"""
        async with self._lock:
            warnings = await self._load_json(self.warnings_file)
            user_id = str(warning_data['user_id'])
            
            if user_id not in warnings:
                warnings[user_id] = []
            
            warnings[user_id].append(warning_data)
            await self._save_json(self.warnings_file, warnings)
    
    async def get_user_warnings(self, user_id: int) -> List[Dict[str, Any]]:
        """Get warnings for a user"""
        warnings = await self._load_json(self.warnings_file)
        return warnings.get(str(user_id), [])
    
    # Deployment Management
    async def save_deployment(self, deployment_data: Dict[str, Any]):
        """Save deployment data"""
        async with self._lock:
            deployments = await self._load_json(self.deployments_file)
            deployments[deployment_data['deployment_id']] = deployment_data
            await self._save_json(self.deployments_file, deployments)
    
    async def get_deployment(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment data by ID"""
        deployments = await self._load_json(self.deployments_file)
        return deployments.get(deployment_id)
    
    # Operation Management
    async def save_operation(self, operation_data: Dict[str, Any]):
        """Save operation data"""
        async with self._lock:
            operations = await self._load_json(self.operations_file)
            operations[operation_data['operation_id']] = operation_data
            await self._save_json(self.operations_file, operations)
    
    async def get_operation(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get operation data by ID"""
        operations = await self._load_json(self.operations_file)
        return operations.get(operation_id)
    
    # Operation Log Management
    async def save_operation_log(self, log_data: Dict[str, Any]):
        """Save operation log data"""
        async with self._lock:
            logs = await self._load_json(self.operation_logs_file)
            log_id = f"{log_data['operation_id']}_{datetime.utcnow().timestamp()}"
            logs[log_id] = log_data
            await self._save_json(self.operation_logs_file, logs)
    
    async def get_operation_logs(self, operation_id: str) -> List[Dict[str, Any]]:
        """Get all logs for an operation"""
        logs = await self._load_json(self.operation_logs_file)
        return [log for log in logs.values() if log.get('operation_id') == operation_id]
    
    # Operator Management
    async def save_operator(self, operator_data: Dict[str, Any]):
        """Save operator data"""
        async with self._lock:
            operators = await self._load_json(self.operators_file)
            operators[str(operator_data['user_id'])] = operator_data
            await self._save_json(self.operators_file, operators)
    
    async def get_operator(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get operator data by user ID"""
        operators = await self._load_json(self.operators_file)
        return operators.get(str(user_id))
    
    async def get_all_operators(self) -> Dict[str, Any]:
        """Get all operators"""
        return await self._load_json(self.operators_file)
    
    # Mission Management
    async def save_mission(self, mission_data: Dict[str, Any]):
        """Save mission data"""
        async with self._lock:
            missions = await self._load_json(self.missions_file)
            missions[mission_data['mission_id']] = mission_data
            await self._save_json(self.missions_file, missions)
    
    async def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission data by ID"""
        missions = await self._load_json(self.missions_file)
        return missions.get(mission_id)
    
    async def get_all_missions(self) -> Dict[str, Any]:
        """Get all missions"""
        return await self._load_json(self.missions_file)
    
    # Cleanup
    async def cleanup_old_data(self, days_old: int = 30):
        """Clean up old data"""
        cutoff_time = datetime.utcnow().timestamp() - (days_old * 24 * 60 * 60)
        
        # Clean up closed tickets
        async with self._lock:
            tickets = await self._load_json(self.tickets_file)
            tickets_to_remove = []
            
            for ticket_id, ticket_data in tickets.items():
                if ticket_data.get('status') == 'closed':
                    closed_at = ticket_data.get('closed_at')
                    if closed_at:
                        closed_timestamp = datetime.fromisoformat(closed_at.replace('Z', '+00:00')).timestamp()
                        if closed_timestamp < cutoff_time:
                            tickets_to_remove.append(ticket_id)
            
            for ticket_id in tickets_to_remove:
                del tickets[ticket_id]
            
            if tickets_to_remove:
                await self._save_json(self.tickets_file, tickets)
    
    # Backup
    async def create_backup(self) -> str:
        """Create a backup of all data"""
        backup_data = {
            'tickets': await self.get_all_tickets(),
            'operators': await self.get_all_operators(),
            'missions': await self.get_all_missions(),
            'deployments': await self._load_json(self.deployments_file),
            'operations': await self._load_json(self.operations_file),
            'operation_logs': await self._load_json(self.operation_logs_file),
            'warnings': await self._load_json(self.warnings_file),
            'backup_timestamp': datetime.utcnow().isoformat()
        }
        
        backup_filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = f"{self.data_dir}/{backup_filename}"
        
        async with aiofiles.open(backup_path, 'w') as f:
            await f.write(json.dumps(backup_data, indent=2))
        
        return backup_path