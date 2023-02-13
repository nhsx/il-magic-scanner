.PHONY: default
default:
	ansible-playbook -i ./hosts ./site.yml

.PHONY: first
first:
	ansible-playbook -i ./hosts ./site.yml -K

.PHONY: sh
sh:
	ssh -tA piscanner.local tmux new-session -AD

.PHONY: backup
backup:
	rsync -avz pi@piscanner.local:src backup/
