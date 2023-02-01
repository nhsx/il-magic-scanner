# Useful GPU provisioning terraform scripts

The terraform and ansible scripts in this directory will provision and
configure a GPU instance (`g3s.xlarge` by default) and a jump host
(`t3.small`) in AWS for machine learning with
[Darknet](https://github.com/AlexeyAB/darknet).

## Usage

Before using this, you will need to set up your `.aws/credentials`
such that terraform can do its thing, you will need a public SSH key
at `~/.ssh/id_rsa.pub`, and you will need to an SSH keypair set up in
the AWS console.  Set that keypair name in the `my_key_pair_name`
variable in `variables.tf`.

Next, you need to modify `main.tf`.  In the state it's stored in this
repository, just running `terraform` *will not* provision a
potentially expensive GPU host.  To do that, you need to open
`main.tf`, go to the end of the file, and find the line which says
`count = 0`.  It's the only `count` setting in the file.  Change it to
`count = 1`.

With those in place, this will show you what terraform is going to do:

    $ make plan

If you're happy that it should go ahead and do that, run:

    $ make terraform

*THIS MARKS THE POINT AT WHICH YOU START BEING CHARGED.  WHEN `make
terraform` HAS FINISHED, IT IS COSTING YOU MONEY.*

Edit your `/etc/hosts` file and add entries called `jumphost` and
`gpuhost` with the IP addresses from terraform's output.  Now, run:

    $ make first

This will configure both `jumphost` and `gpuhost` with some
convenience packages and, importantly, it will install `darknet` on
`gpuhost`.  `make first` needs to ask you for the sudo password for
each host, but if you subsequently need to run `ansible` again, you
can just run `make` alone: the default task runs `ansible` with no
password needed.

Now you can `ssh` to `jumphost`, copy data to `gpuhost`, and run
`darknet` to your heart's desires.

### Tidying up

When you have finished your learning on `gpuhost`, you have retrieved
any artefacts you want, and you are absolutely certain that don't need
the instance any more, the way to shut it down is to edit `main.tf`,
change `count = 1` to `count =0`, and then run `make terraform` again.
This has the effect of removing the spot instance request, while
leaving the jump host intact.

*THIS IS STILL COSTING YOU MONEY, JUST LESS OF IT.*

There is no `make` task to completely tear down the terraformed
infrastructure.  If you do want to do that, running `terraform
destroy` will do so.
