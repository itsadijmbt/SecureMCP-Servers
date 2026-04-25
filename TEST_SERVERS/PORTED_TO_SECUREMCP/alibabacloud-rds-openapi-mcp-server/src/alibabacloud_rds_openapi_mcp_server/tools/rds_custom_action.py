# -*- coding: utf-8 -*-
"""Provides the 'Action' or 'Write-Enabled' functionalities for the 'rds_custom' toolset.

This module, packaged as `rds_custom_action`, contains all interfaces that
modify resource states (e.g., Create, Stop, Delete).

It serves as an **extension** to the `rds_custom_read` toolset and **cannot
be used stand-alone**. For detailed loading logic and scenarios, please
refer to the documentation in the `rds_custom_read` module.
"""
import logging
from typing import Dict, Any, Optional, List
import alibabacloud_rds20140815.models as RdsApiModels

from .aliyun_openapi_gateway import AliyunServiceGateway
from . import tool

logger = logging.getLogger(__name__)

RDS_CUSTOM_GROUP_NAME = 'rds_custom_action'

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def resize_rc_instance_disk(
    region_id: str,
    instance_id: str,
    new_size: int,
    disk_id: str,
    auto_pay: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    resize a specific rds custom instance's disk.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        new_size: The target size of the disk in GiB.
        disk_id: The ID of the cloud disk.
        auto_pay: Specifies whether to enable automatic payment. Default is false.
        dry_run: Specifies whether to perform a dry run. Default is false.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.ResizeRCInstanceDiskRequest(
        region_id=region_id,
        instance_id=instance_id,
        new_size=new_size,
        disk_id=disk_id,
        auto_pay=auto_pay,
        dry_run=dry_run,
        type='online'
    )
    return AliyunServiceGateway(region_id).rds().resize_rcinstance_disk_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def modify_rc_instance_attribute(
    region_id: str,
    instance_id: str,
    password: Optional[str] = None,
    reboot: Optional[bool] = None,
    host_name: Optional[str] = None,
    security_group_id: Optional[str] = None,
    deletion_protection: Optional[bool] = None
) -> Dict[str, Any]:
    """
    modify attributes of a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance to modify.
        password: The new password for the instance.
        reboot: Specifies whether to restart the instance after modification.
        host_name: The new hostname for the instance.
        security_group_id: The ID of the new security group for the instance.
        deletion_protection: Specifies whether to enable the deletion protection feature.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.ModifyRCInstanceAttributeRequest(
        region_id=region_id,
        instance_id=instance_id,
        password=password,
        reboot=reboot,
        host_name=host_name,
        security_group_id=security_group_id,
        deletion_protection=deletion_protection
    )
    return AliyunServiceGateway(region_id).rds().modify_rcinstance_attribute_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def stop_rc_instances(
    region_id: str,
    instance_ids: List[str],
    force_stop: bool = False,
    batch_optimization: Optional[str] = None
) -> Dict[str, Any]:
    """
    stop one or more rds custom instances in batch.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_ids: A list of instance IDs to be stopped.
        force_stop: Specifies whether to force stop the instances. Default is false.
        batch_optimization: The batch operation mode.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.StopRCInstancesRequest(
        region_id=region_id,
        instance_ids=instance_ids,
        force_stop=force_stop,
        batch_optimization=batch_optimization
    )
    return AliyunServiceGateway(region_id).rds().stop_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def start_rc_instances(
    region_id: str,
    instance_ids: List[str],
    batch_optimization: Optional[str] = None
) -> Dict[str, Any]:
    """
    start one or more rds custom instances in batch.

    Args:
        region_id: The region ID of the RDS Custom instances.
        instance_ids: A list of instance IDs to be started.
        batch_optimization: The batch operation mode.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.StartRCInstancesRequest(
        region_id=region_id,
        instance_ids=instance_ids,
        batch_optimization=batch_optimization
    )
    return AliyunServiceGateway(region_id).rds().start_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def reboot_rc_instance(
    region_id: str,
    instance_id: str,
    force_stop: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    reboot a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to reboot.
        force_stop: Specifies whether to force shutdown before rebooting. Default is false.
        dry_run: Specifies whether to perform a dry run only. Default is false.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.RebootRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        force_stop=force_stop,
        dry_run=dry_run
    )
    return AliyunServiceGateway(region_id).rds().reboot_rcinstance_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def modify_rc_instance_description(
    region_id: str,
    instance_id: str,
    instance_description: str
) -> Dict[str, Any]:
    """
    modify the description of a specific rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the instance to modify.
        instance_description: The new description for the instance.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """

    request = RdsApiModels.ModifyRCInstanceDescriptionRequest(
        region_id=region_id,
        instance_id=instance_id,
        instance_description=instance_description
    )
    return AliyunServiceGateway(region_id).rds().modify_rcinstance_description_with_options(request)



@tool(group=RDS_CUSTOM_GROUP_NAME)
async def sync_rc_security_group(
    region_id: str,
    instance_id: str,
    security_group_id: str
) -> Dict[str, Any]:
    """
    synchronize the security group rules for an rds sql server custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        security_group_id: The ID of the security group.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.SyncRCSecurityGroupRequest(
        region_id=region_id,
        instance_id=instance_id,
        security_group_id=security_group_id
    )

    return AliyunServiceGateway(region_id).rds().sync_rcsecurity_group_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def associate_eip_address_with_rc_instance(
    region_id: str,
    instance_id: str,
    allocation_id: str
) -> Dict[str, Any]:
    """
    associate an elastic ip address (eip) with an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        allocation_id: The ID of the Elastic IP Address.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.AssociateEipAddressWithRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        allocation_id=allocation_id
    )

    return AliyunServiceGateway(region_id).rds().associate_eip_address_with_rcinstance_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def create_rc_snapshot(
    region_id: str,
    disk_id: str,
    description: Optional[str] = None,
    retention_days: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a manual snapshot for a specific cloud disk of an RDS Custom instance.

    Args:
        region_id: The region ID. You can call DescribeRegions to obtain the latest region list.
        disk_id: The ID of the cloud disk for which to create a snapshot.
        description: The description of the snapshot. It must be 2 to 256 characters in length and cannot start with http:// or https://.
        retention_days: The retention period of the snapshot, in days. After the retention period expires, the snapshot is automatically released. Value range: 1 to 65536.

    Returns:
        dict[str, Any]: A dictionary containing the RequestId and the ID of the new snapshot.
    """
    request = RdsApiModels.CreateRCSnapshotRequest(
        region_id=region_id,
        disk_id=disk_id,
        description=description,
        retention_days=retention_days
    )

    return AliyunServiceGateway(region_id).rds().create_rcsnapshot_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def run_rc_instances(
        region_id: str,
        instance_type: str,
        password: str,
        vswitch_id: str,
        security_group_id: str,
        zone_id: str,
        image_id: str,
        # --- Optional Parameters ---
        instance_charge_type: Optional[str] = None,
        amount: Optional[int] = None,
        period: Optional[int] = None,
        period_unit: Optional[str] = None,
        auto_renew: Optional[bool] = None,
        auto_pay: Optional[bool] = None,
        client_token: Optional[str] = None,
        auto_use_coupon: Optional[bool] = None,
        promotion_code: Optional[str] = None,
        data_disk: Optional[List[Dict[str, Any]]] = None,
        system_disk: Optional[Dict[str, Any]] = None,
        deployment_set_id: Optional[str] = None,
        internet_max_bandwidth_out: Optional[int] = None,
        description: Optional[str] = None,
        key_pair_name: Optional[str] = None,
        dry_run: Optional[bool] = None,
        tag: Optional[List[Dict[str, str]]] = None,
        resource_group_id: Optional[str] = None,
        create_mode: Optional[str] = None,
        host_name: Optional[str] = None,
        spot_strategy: Optional[str] = None,
        support_case: Optional[str] = None,
        create_ack_edge_param: Optional[Dict[str, Any]] = None,
        user_data: Optional[str] = None,
        user_data_in_base_64: Optional[bool] = None,
        deletion_protection: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Creates one or more RDS Custom instances by converting dicts to model objects internally.

    Args:
        region_id: The region ID.
        instance_type: The instance specification. See RDS Custom instance specification list for details.
        password: The password for the instance. It must be 8 to 30 characters long and contain at least three of the following character types: uppercase letters, lowercase letters, digits, and special characters.
        vswitch_id: The vSwitch ID for the target instance.
        security_group_id: The ID of the security group to which the instance belongs.
        zone_id: The zone ID to which the instance belongs.
        image_id: The image ID used by the instance.
        instance_charge_type: The billing method. Valid values: Prepaid (subscription), PostPaid (pay-as-you-go).
        amount: The number of RDS Custom instances to create. Default is 1.
        period: The subscription duration of the resource. Used when instance_charge_type is 'Prepaid'.
        period_unit: The unit of the subscription duration. Valid values: Month, Year.
        auto_renew: Specifies whether to enable auto-renewal for the subscription.
        auto_pay: Specifies whether to enable automatic payment.
        client_token: A client token used to ensure the idempotence of the request.
        auto_use_coupon: Specifies whether to automatically use coupons.
        promotion_code: The coupon code.
        data_disk: The list of data disks. Example: [{"Size": 50, "Category": "cloud_essd"}]
        system_disk: The system disk specification. Example: {"Size": 60, "Category": "cloud_essd"}
        deployment_set_id: The deployment set ID.
        internet_max_bandwidth_out: The maximum public outbound bandwidth in Mbit/s for Custom for SQL Server.
        description: The description of the instance.
        key_pair_name: The name of the key pair.
        dry_run: Specifies whether to perform a dry run to check the request.
        tag: A list of tags to attach to the instance. Example: [{"Key": "your_key", "Value": "your_value"}].
        resource_group_id: The resource group ID.
        create_mode: Whether to allow joining an ACK cluster. '1' means allowed.
        host_name: The hostname of the instance.
        spot_strategy: The bidding strategy for the pay-as-you-go instance.
        support_case: The RDS Custom edition. 'share' or 'exclusive'.
        create_ack_edge_param: Information for the ACK Edge cluster.
        user_data: Custom data for the instance, up to 32 KB in raw format.
        user_data_in_base_64: Whether the custom data is Base64 encoded.
        deletion_protection: Specifies whether to enable release protection.

    Returns:
        dict[str, Any]: A dictionary containing the OrderId, RequestId, and the set of created instance IDs.
    """
    system_disk_obj = None
    if system_disk:
        system_disk_obj = RdsApiModels.RunRCInstancesRequestSystemDisk(**system_disk)
    data_disk_objs = None
    if data_disk:
        data_disk_objs = [RdsApiModels.RunRCInstancesRequestDataDisk(**disk) for disk in data_disk]
    tag_objs = None
    if tag:
        tag_objs = [RdsApiModels.RunRCInstancesRequestTag(**t) for t in tag]
    request = RdsApiModels.RunRCInstancesRequest(
        region_id=region_id,
        instance_type=instance_type,
        password=password,
        v_switch_id=vswitch_id,
        security_group_id=security_group_id,
        zone_id=zone_id,
        image_id=image_id,
        instance_charge_type=instance_charge_type,
        amount=amount,
        period=period,
        period_unit=period_unit,
        auto_renew=auto_renew,
        auto_pay=auto_pay,
        client_token=client_token,
        auto_use_coupon=auto_use_coupon,
        promotion_code=promotion_code,
        deployment_set_id=deployment_set_id,
        internet_max_bandwidth_out=internet_max_bandwidth_out,
        description=description,
        key_pair_name=key_pair_name,
        dry_run=dry_run,
        resource_group_id=resource_group_id,
        create_mode=create_mode,
        host_name=host_name,
        spot_strategy=spot_strategy,
        support_case=support_case,
        create_ack_edge_param=create_ack_edge_param,
        user_data=user_data,
        user_data_in_base_64=user_data_in_base_64,
        deletion_protection=deletion_protection,
        system_disk=system_disk_obj,
        data_disk=data_disk_objs,
        tag=tag_objs
    )
    return AliyunServiceGateway(region_id).rds().run_rcinstances_with_options(request)

@tool(group=RDS_CUSTOM_GROUP_NAME)
async def unassociate_eip_address_with_rc_instance(
    region_id: str,
    instance_id: str,
    allocation_id: str
) -> Dict[str, Any]:
    """
    unassociate an elastic ip address (eip) from an rds custom instance.

    Args:
        region_id: The region ID of the RDS Custom instance.
        instance_id: The ID of the RDS Custom instance.
        allocation_id: The ID of the Elastic IP Address to unassociate.

    Returns:
        dict[str, Any]: The response containing the result of the operation.
    """
    request = RdsApiModels.UnassociateEipAddressWithRCInstanceRequest(
        region_id=region_id,
        instance_id=instance_id,
        allocation_id=allocation_id
    )

    return AliyunServiceGateway(region_id).rds().unassociate_eip_address_with_rcinstance_with_options(request)
