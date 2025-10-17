Used commands

List available flavors	openstack flavor list --max-width 500
List images	openstack image list --max-width 500
List keypairs	openstack keypair list --max-width 500
List security groups	openstack security group list -c ID -c Name --max-width 500
List networks	openstack network list -c ID -c Name --max-width 500

Create a floating IP	openstack floating ip create --description <description> public
Attach floating IP	openstack server add floating ip <server_name> <ip_id>

Create a baremetal machine	openstack server create --flavor baremetal --image <image_id> --key-name <key_name> --security-group <sec_group> --hint reservation=<reservation_id> --property reservation_id=<lease_id> --network <network_id> <machine_name>

Create a virtual machine	openstack server create --flavor <flavor> --image <image_id> --key-name <key_name> --security-group <sec_group> --network <network_id> <machine_name>

List active servers (filters by ACTIVE status)	openstack server list -c ID -c Name -c Networks -c Status --max-width 500

Delete server	openstack server delete <server_name> -v
Delete floating IP	openstack floating ip delete <ip_address>

Create new reservation lease (baremetal)	openstack reservation lease create --reservation min=1,max=1,resource_type=physical:host,resource_properties='["=", "$node_type", "<node_type>"]' --start-date "now" --end-date "<end_date> <end_time>" <machine_name> -c reservations





