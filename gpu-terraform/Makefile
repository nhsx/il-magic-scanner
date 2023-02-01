.PHONY: default
default:
	ansible-playbook -i ./hosts ./site.yml

.terraform-has-inited:
	terraform init
	touch .terraform-has-inited

.PHONY: terraform
terraform: .terraform-has-inited
	terraform apply

.PHONY: plan
plan: .terraform-has-inited
	terraform plan

.PHONY: first
first:
	ansible-playbook -i ./hosts ./site.yml -K

.PHONY: sh
sh:
	ssh -tA ubuntu@jumphost tmux new-session -AD

.PHONY: backup
backup:
	rsync -avz ubuntu@jumphost:~/ backup/
