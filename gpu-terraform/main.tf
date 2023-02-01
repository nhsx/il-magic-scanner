provider "aws" {
  region = "${var.my_region}"
}

locals {
  avail_zone = "${var.avail_zone}"
}

resource "aws_vpc" "main_vpc" {
  cidr_block = "${var.my_cidr_block}"
  instance_tenancy = "default"
  enable_dns_hostnames = true

  tags = {
    Name = "il_vpc"
  }
}

resource "aws_internet_gateway" "main_vpc_igw" {
  vpc_id = "${aws_vpc.main_vpc.id}"

  tags = {
    Name = "il_vpc_igw"
  }
}

resource "aws_default_route_table" "main_vpc_default_route_table" {
  default_route_table_id = "${aws_vpc.main_vpc.default_route_table_id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.main_vpc_igw.id}"
  }

  tags = {
    Name = "il_vpc_default_route_table"
  }
}

resource "aws_subnet" "main_vpc_subnet" {
  vpc_id = "${aws_vpc.main_vpc.id}"
  cidr_block = "${var.my_cidr_block}"
  map_public_ip_on_launch = true
  availability_zone  = "${local.avail_zone}"

  tags = {
    Name = "il_vpc_subnet"
  }
}

resource "aws_default_network_acl" "main_vpc_nacl" {
  default_network_acl_id = "${aws_vpc.main_vpc.default_network_acl_id}"
  subnet_ids = ["${aws_subnet.main_vpc_subnet.id}"]

  ingress {
    protocol   = -1
    rule_no    = 1
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  egress {
    protocol   = -1
    rule_no    = 2
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = "il_vpc_nacl"
  }
}

resource "aws_default_security_group" "main_vpc_security_group" {
  vpc_id = "${aws_vpc.main_vpc.id}"

  # SSH access from anywhere
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"]
  }

  # Jupyter
  ingress {
    from_port = 8888
    to_port = 8888
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  # git clone
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = {
    Name = "il_vpc_security_group"
  }
}

# This is the image we're using for the jump host.  I don't
# want to have to faff about with the AMI ID for this one because there are
# fairly frequent rebuilds.  The AMI ID for the gpu host is in variables.tf.
data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"]
}

resource "aws_instance" "jump_host" {
  ami = data.aws_ami.ubuntu.id

  instance_type = "${var.instance_type}"
  key_name = "${var.my_key_pair_name}"
  associate_public_ip_address = true
  vpc_security_group_ids = ["${aws_default_security_group.main_vpc_security_group.id}"]
  subnet_id = "${aws_subnet.main_vpc_subnet.id}"
  root_block_device {
    volume_size = "${var.ebs_volume_size}"
    volume_type = "gp2"
  }

  tags = {
    Name = "Jump host"
  }
}

resource "aws_eip" "jump_host_ip" {
  instance = aws_instance.jump_host.id
  vpc = true
}


# After all that, this is the resource which defines the actual GPU instance.
# The presence or absence of the instance is controlled by the `count` field.
# When you want to spin up a GPU instance, set `count` to `1` and run `make
# terraform`.  When you're done with it and have taken all your data off it,
# set `count` to `0` and run `make terraform` again.  Doing it this way means
# the jump host above stays live.
#
resource "aws_spot_instance_request" "aws_dl_custom_spot" {
  ami                         = "${var.ml_ami_id}"
  spot_price                  = "${var.ml_spot_price}"
  instance_type               = "${var.ml_instance_type}"
  key_name                    = "${var.my_key_pair_name}"
  wait_for_fulfillment = true
  spot_type = "one-time"

  associate_public_ip_address = true
  count                       = 0
  security_groups             = ["${aws_default_security_group.main_vpc_security_group.id}"]
  subnet_id                   = "${aws_subnet.main_vpc_subnet.id}"
  ebs_block_device {
    device_name = "/dev/sdh"
    volume_size = "${var.ebs_volume_size}"
    volume_type = "gp2"
  }
  tags = {
    Name = "ML box"
  }
}
