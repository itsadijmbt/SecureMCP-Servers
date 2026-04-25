# -*- coding: utf-8 -*-

from . import prompt
from typing import List, Dict


@prompt(group="rds_custom")
def rds_custom_system_prompt() -> List[Dict[str, str]]:
    """
    Provides a system prompt that defines the role, goals, and core instructions
    for the CloudOps-Assistant AI. This sets the context and operating rules for the assistant.

    Returns:
        A list containing a dictionary that defines the 'system' role and its content.
    """
    return [
        {
            "role": "system",
            "content": r'''
# Role and Goal
You are CloudOps-Assistant, an AI assistant specializing in Alibaba Cloud RDS Custom instance management. Your primary goal is to help users manage their database infrastructure safely and efficiently.

# Core Instructions
1.  **Clarity First:** Before executing any command, repeat the user's intention and the exact parameters you will use.
2.  **Safety Confirmation:** For any action that modifies or deletes a resource (e.g., stop, reboot, resize, modify), you MUST ask for the user's explicit confirmation before proceeding.
3.  **Structured Output:** Present complex information, like lists of instances or metrics, in a clean, readable format using Markdown tables or lists.
4.  **Parameter Requirement:** If a user's request is missing mandatory parameters (like `region_id`), you must ask for them clearly. Do not make assumptions about the region.

'''
        }
    ]


@prompt(group="rds_custom")
def rds_custom_sql_server_health_check_template(instance_id: str, region_id: str) -> str:
    """
    Generates a structured, multi-step instructional string to perform
    a comprehensive health check on a specified RDS instance.

    Args:
        instance_id: The ID of the RDS instance to be checked.
        region_id: The region where the RDS instance is located.

    Returns:
        A formatted string that serves as a detailed input prompt for the user,
        outlining the steps for a health check.
    """
    # The function returns a string that will be used as the 'input' from the user.
    # {instance_id} and {region_id} are placeholders that the MCP framework will populate.
    return f"""
Please perform a complete health check for the RDS instance with the following steps:

1.  **Query Basic Instance Information**: Use the `describe_rc_instance_attribute` tool to query the detailed attributes of instance `{instance_id}` in region `{region_id}`, focusing on its status, specifications, and creation time.
2.  **Check CPU and Memory**: Use the `describe_rc_metric_list` tool to retrieve the `CPUUtilization` and `MemoryUsage` metrics for the instance over the last 3 hours.
3.  **Check Disk Space**: Use the `describe_rc_metric_list` tool to retrieve the `DiskUsage` metric for the instance.
4.  **Summary Report**: Based on all the information gathered above, generate a health summary report for me and point out any potential risks.
"""