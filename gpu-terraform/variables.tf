variable "my_region" {
  default = "eu-west-2"
}

variable "avail_zone" {
  default = "eu-west-2a"
}

variable "my_cidr_block" {
  default = "10.0.0.0/24"
}

variable "my_key_pair_name" {
  default = "YOUR KEYPAIR NAME HERE"
}

variable "ssh-key-dir" {
  default = "~/.ssh/"
}

# The instance type for the jump host.  Just enough grunt to be useful.
variable "instance_type" {
  default = "t3.small"

}

# The instance type for the GPU instance.  This is the GPU instance type which
# had the cheapest spot rate at the time.
variable "ml_instance_type" {
  default = "g3s.xlarge"

}

variable "ml_spot_price" {
  default = "0.30"
}

# Default AWS Deep Learning AMI (Ubuntu)
variable "ml_ami_id" {
  default = "ami-09c51a13d5ada2047" 
}

# You definitely need more room than the default.
variable "ebs_volume_size" {
  default = "30"
}

variable "num_instances" {
  default = "1"
}
