# -*- coding: utf-8 -*-
"""Provides the core 'Read-Only' functionalities for the "rds_custom" MCP toolset.

This module exclusively contains all "Describe*" class interfaces, packaged as
the **`rds_custom_read`** toolset.

The `rds_custom_read` group is the foundational layer for all operations. It
allows for safe, comprehensive environmental analysis (querying, auditing,
monitoring) and can be loaded stand-alone. To perform any actions that modify
resources (e.g., create, stop, delete), this `rds_custom_read` toolset MUST be
loaded alongside the `rds_custom_action` toolset

Toolsets are loaded at runtime via the `--toolsets` command-line argument
or a corresponding environment variable.

Command-Line Usage and Scenarios:
---------------------------------
1.  **Read-Only Operations:**
    To load only the query and describe functionalities, specify the
    `rds_custom_read` group. This is a safe, view-only mode.

2.  **Full Access / Read-Write Operations (Management, Execution):**
    To perform actions, you MUST load **both** the `rds_custom_read` group
    (to find and verify targets) AND the `rds_custom_action` group (to
    execute changes). shortcut is `rds_custom_all`

Command-Line Examples:
----------------------
# Scenario 1: Load the read-only toolset for auditing.
# python server.py --toolsets rds_custom_read

# Scenario 2: Load both read and action toolsets for full management capabilities.
# python server.py --toolsets rds_custom_all
"""

import logging
from typing import Dict, Any, Optional, List
import alibabacloud_rds20140815.models as RdsApiModels
from .aliyun_openapi_gateway import AliyunServiceGateway
from . import tool


logger = logging.getLogger(__name__)

RDS_CUSTOM_GROUP_NAME = 'rds_custom_read'

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instances(region_id: str, instance_id: str|None = None) -> Dict[str, Any]:
    """
    describe rds custom instances.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_id: The ID of a specific instance. If omitted, all instances in the region are returned.

    Returns:
        dict[str, Any]: The response containing instance metadata.
    """
    request = RdsApiModels.DescribeRCInstancesRequest(
        region_id=region_id,
        instance_id=instance_id
    )
    rds_client = AliyunServiceGateway(region_id).rds()
    return rds_client.describe_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instance_attribute(region_id: str,instance_id: str) -> Dict[str, Any]:
    """
    describe a single rds custom instance's details.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.

    Returns:
        dict[str, Any]: The response containing the instance details.
    """
    request = RdsApiModels.DescribeRCInstanceAttributeRequest(
        region_id=region_id,
        instance_id=instance_id
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_attribute_with_options(request)


@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instance_vnc_url(
    region_id: str,
    instance_id: str,
    db_type: str
) -> Dict[str, Any]:
    """
    describe the vnc login url for a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance.
        db_type: The database type, e.g., 'mysql' or 'mssql'.

    Returns:
        dict[str, Any]: The response containing the VNC login URL.
    """
    request = RdsApiModels.DescribeRCInstanceVncUrlRequest(
        region_id=region_id,
        instance_id=instance_id,
        db_type=db_type
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_vnc_url_with_options(request)


@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instance_ip_address(
    region_id: str,
    instance_id: str,
    ddos_region_id: str,
    instance_type: str = 'ecs',
    resource_type: str = 'ecs',
    ddos_status: Optional[str] = None,
    instance_ip: Optional[str] = None,
    current_page: Optional[int] = None,
    page_size: Optional[int] = None,
    instance_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe the ddos protection details for an rds custom instance.
    Args:
        region_id: The region ID where the Custom instance is located.
        instance_id: The ID of the Custom instance.
        ddos_region_id: The region ID of the public IP asset.
        instance_type: The instance type of the public IP asset, fixed value 'ecs'.
        resource_type: The resource type, fixed value 'ecs'.
        ddos_status: The DDoS protection status of the public IP asset.
        instance_ip: The IP address of the public IP asset to query.
        current_page: The page number of the results to display.
        page_size: The number of instances per page.
        instance_name: The name of the Custom instance.

    Returns:
        dict[str, Any]: The response containing the DDoS protection details.
    """
    request = RdsApiModels.DescribeRCInstanceIpAddressRequest(
        region_id=region_id,
        instance_id=instance_id,
        ddos_region_id=ddos_region_id,
        instance_type=instance_type,
        resource_type=resource_type,
        ddos_status=ddos_status,
        instance_ip=instance_ip,
        current_page=current_page,
        page_size=page_size,
        instance_name=instance_name
    )
    return AliyunServiceGateway(region_id).rds().describe_rcinstance_ip_address_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_image_list(
    region_id: str,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    type: Optional[str] = None,
    architecture: Optional[str] = None,
    image_id: Optional[str] = None,
    image_name: Optional[str] = None,
    instance_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe the list of custom images for creating rds custom instances.

    Args:
        region_id: The region ID to query for images.
        page_number: The page number of the results.
        page_size: The number of records per page.
        type: The image type, currently only 'self' is supported.
        architecture: The system architecture of the image, e.g., 'x86_64'.
        image_id: The ID of a specific image to query.
        image_name: The name of a specific image to query.
        instance_type: The instance type to query usable images for.

    Returns:
        dict[str, Any]: The response containing the list of custom images.
    """
    request = RdsApiModels.DescribeRCImageListRequest(
        region_id=region_id,
        page_number=page_number,
        page_size=page_size,
        type=type,
        architecture=architecture,
        image_id=image_id,
        image_name=image_name,
        instance_type=instance_type
    )

    return AliyunServiceGateway(region_id).rds().describe_rcimage_list_with_options(request)


@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_snapshots(
    region_id: str,
    disk_id: Optional[str] = None,
    snapshot_ids: Optional[List[str]] = None,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Query the list of RDS Custom snapshots information.

    Args:
        region_id: The region ID. You can call DescribeRegions to obtain the latest region list.
        disk_id: The specified cloud disk ID.
        snapshot_ids: The list of snapshot IDs.
        page_number: The page number to return.
        page_size: The number of entries to return on each page. Value range: 30~100. Default value: 30.

    Returns:
        dict[str, Any]: The response containing the list of snapshots and pagination information.
    """

    request = RdsApiModels.DescribeRCSnapshotsRequest(
        region_id=region_id,
        disk_id=disk_id,
        snapshot_ids=snapshot_ids,
        page_number=page_number,
        page_size=page_size
    )

    return AliyunServiceGateway(region_id).rds().describe_rcsnapshots_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_metric_list(
    region_id: str,
    instance_id: str,
    metric_name: str,
    start_time: str,
    end_time: str,
    period: Optional[str] = None,
    length: Optional[str] = None,
    next_token: Optional[str] = None,
    dimensions: Optional[str] = None,
    express: Optional[str] = None
) -> Dict[str, Any]:
    """
    describe monitoring data for a specific metric of an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to query.
        metric_name: The metric to be monitored, e.g., 'CPUUtilization'.
        start_time: The start time of the query, format 'YYYY-MM-DD HH:MM:SS'.
        end_time: The end time of the query, format 'YYYY-MM-DD HH:MM:SS'.
        period: The statistical period of the monitoring data in seconds.
        length: The number of entries to return on each page.
        next_token: The pagination token.
        dimensions: The dimensions to query data for multiple resources in batch.
        express: A reserved parameter.

    Returns:
        dict[str, Any]: The response containing the list of monitoring data.
    """
    request = RdsApiModels.DescribeRCMetricListRequest(
        region_id=region_id,
        instance_id=instance_id,
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time,
        period=period,
        length=length,
        next_token=next_token,
        dimensions=dimensions,
        express=express
    )

    return AliyunServiceGateway(region_id).rds().describe_rcmetric_list_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_disks(
    region_id: str,
    instance_id: Optional[str] = None,
    disk_ids: Optional[List[str]] = None,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    tag: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Query the list of disks for an RDS Custom instance.

    Args:
        region_id: The region ID. You can call DescribeRegions to obtain the latest region list.
        instance_id: The ID of the instance to which the disks belong.
        disk_ids: The list of disk IDs to query. Supports up to 100 IDs.
        page_number: The page number to return.
        page_size: The number of entries to return on each page. Value range: 30 to 100. Default value: 30.
        tag: A list of tags to filter results. For example: [{"Key": "your_key", "Value": "your_value"}].

    Returns:
        dict[str, Any]: A dictionary containing the list of disks and pagination information.
    """
    request = RdsApiModels.DescribeRCDisksRequest(
        region_id=region_id,
        instance_id=instance_id,
        disk_ids=disk_ids,
        page_number=page_number,
        page_size=page_size,
        tag=tag
    )
    return AliyunServiceGateway(region_id).rds().describe_rcdisks_with_options(request)


@tool(group=RDS_CUSTOM_GROUP_NAME)
async def describe_rc_instance_ddos_count(
    region_id: str,
    ddos_region_id: str,
    instance_type: str = 'ecs'
) -> Dict[str, Any]:
    """
    describe the count of ddos attacks on rds custom instances.

    Args:
        region_id: The region ID where the Custom instance is located.
        ddos_region_id: The region ID of the public IP asset to query.
        instance_type: The instance type of the public IP asset, fixed value 'ecs'.

    Returns:
        dict[str, Any]: The response containing the count of ddos attacks.
    """
    request = RdsApiModels.DescribeRCInstanceDdosCountRequest(
        region_id=region_id,
        ddos_region_id=ddos_region_id,
        instance_type=instance_type
    )

    return AliyunServiceGateway(region_id).rds().describe_rcinstance_ddos_count_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def get_current_time() -> Dict[str, Any]:
    """Get the current time.

    Returns:
        Dict[str, Any]: The response containing the current time.
    """
    import datetime
    try:
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "current_time": formatted_time
        }
    except Exception as e:
        logger.error(f"Error occurred while getting the current time: {str(e)}")
        raise Exception(f"Failed to get the current time: {str(e)}")
