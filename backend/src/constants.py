"""Constants used throughout the Cloud Pilot application."""

# Node/Edge names
NODE_ANALYZE_TERRAFORM = "analyze_terraform"
NODE_GENERATE_TERRAFORM = "generate_terraform"
NODE_EXECUTE_TERRAFORM = "execute_terraform"
NODE_FILE_SYSTEM_OPERATIONS = "file_system_operations"
NODE_USER_INTERACTION = "user_interaction"
NODE_TERRAFORM_PLAN = "terraform_plan"
NODE_PLAN_APPROVAL = "plan_approval"

# Action names (used in next_action)
ACTION_ANALYZE = "analyze"
ACTION_GENERATE = "generate"
ACTION_EXECUTE = "execute"
ACTION_FILE_OPS = "file_ops"
ACTION_PLAN = "plan"
ACTION_APPROVE_PLAN = "approve_plan"
ACTION_USER_INTERACTION = "user_interaction"
ACTION_END = "end"