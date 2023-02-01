output "name" {
  value=["${aws_instance.jump_host.public_dns}"]
}

output "ip_address" {
  value=["${aws_eip.jump_host_ip.public_ip}"]
}

output "status" {
  value=["${aws_instance.jump_host.instance_state}"]
}
