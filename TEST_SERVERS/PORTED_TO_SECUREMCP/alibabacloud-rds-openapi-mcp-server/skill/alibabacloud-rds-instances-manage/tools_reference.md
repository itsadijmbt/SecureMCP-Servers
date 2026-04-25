# Alibabacloud RDS Instances Manage 工具参考

以下为 `alibabacloud-rds-instances-manage list` 默认工具集（`rds`）中的工具名及主要参数说明，便于大模型构造 `alibabacloud-rds-instances-manage run <name> '<json>'` 的 JSON。

## OpenAPI 只读类

- **describe_db_instances**  
  - `region_id`: 地域，如 cn-hangzhou

- **describe_db_instance_attribute**  
  - `region_id`, `db_instance_id`

- **describe_available_zones**  
  - `region_id`, `engine`, `engine_version`, `instance_charge_type` 等

- **describe_available_classes**  
  - `region_id`, `zone_id`, `instance_charge_type`, `engine`, `engine_version`, `dbinstance_storage_type`, `category`；可选 `dbinstance_id`, `order_type`, `commodity_code`

- **describe_db_instance_performance**  
  - `region_id`, `db_instance_id`, `db_type`, `perf_keys`(数组), `start_time`, `end_time`

- **describe_monitor_metrics**  
  - 通过 DAS 查询监控；需 `region_id`, `db_instance_id`, 时间范围等

- **describe_slow_log_records**  
  - `region_id`, `db_instance_id`, `start_time`, `end_time` 等

- **describe_error_logs**  
  - `region_id`, `db_instance_id`, 时间等

- **describe_db_instance_parameters**  
  - `region_id`, `db_instance_id`

- **describe_db_instance_databases**  
  - `region_id`, `db_instance_id`

- **describe_db_instance_accounts**  
  - `region_id`, `db_instance_id`

- **describe_db_instance_net_info**  
  - `region_id`, `db_instance_id`

- **describe_db_instance_ip_allowlist**  
  - `region_id`, `db_instance_id`

- **describe_vpcs**  
  - `region_id` 等

- **describe_vswitches**  
  - `region_id`, `vpc_id` 等

- **describe_bills**  
  - 账单查询，需计费周期等参数

- **describe_all_whitelist_template** / **describe_instance_linked_whitelist_template**  
  - 白名单模板相关

- **get_current_time**  
  - 无参数，传 `{}`

- **describe_sql_insight_statistic**  
  - SQL 洞察统计

## OpenAPI 写类

- **create_db_instance**  
  - `region_id`, `engine`, `engine_version`, `dbinstance_class`, `dbinstance_storage`, `vpc_id`, `vswitch_id`, `zone_id` 等

- **modify_parameter**  
  - `region_id`, `dbinstance_id`, `parameters`(JSON 键值), 可选 `forcerestart`, `switch_time_mode`, `switch_time`

- **modify_db_instance_spec**  
  - `region_id`, `dbinstance_id`，以及规格/存储/付费类型等

- **modify_db_instance_description**  
  - `region_id`, `dbinstance_id`, `description`

- **create_db_instance_account**  
  - `region_id`, `dbinstance_id`, 账号名与密码等

- **modify_security_ips**  
  - `region_id`, `dbinstance_id`, 白名单配置

- **allocate_instance_public_connection**  
  - 分配公网连接

- **attach_whitelist_template_to_instance**  
  - 白名单模板绑定实例

- **add_tags_to_db_instance**  
  - 为实例打标签

- **restart_db_instance**  
  - `region_id`, `dbinstance_id`

## SQL 类（只读）

- **query_sql**  
  - `region_id`, `db_instance_id`, `db_name`, `sql`

- **explain_sql**  
  - `region_id`, `db_instance_id`, `db_name`, `sql`

- **show_create_table**  
  - `region_id`, `db_instance_id`, `db_name`, `table_name`

- **show_engine_innodb_status**  
  - `region_id`, `db_instance_id`

- **show_largest_table**  
  - `region_id`, `db_instance_id`, 可选 `topK`（默认 5）

- **show_largest_table_fragment**  
  - `region_id`, `db_instance_id`, 可选 `topK`

参数名以各工具在代码中的定义为准；不确定时可先 `alibabacloud-rds-instances-manage list` 查看描述，再按文档构造 JSON。