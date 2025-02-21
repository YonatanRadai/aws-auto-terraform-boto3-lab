import jinja2
from ami_dict import ami_dict

class TerraformCreator:
    def __init__(self):
        self.selections = {}

    def take_input(self):
        # Prompt user for Region selection
        region = input("Select Region (us-east-1, us-west-1): ")
        if region not in ["us-east-1", "us-west-1"]:
            print("Invalid Region selection. Defaulting to us-east-1.")
            region = "us-east-1"

        # Filter AMIs based on the selected region
        filtered_ami_dict = {k: v for k, v in ami_dict.items() if k[1] == region}

        # Prompt user for AMI selection
        ami_options = ", ".join([ami[0] for ami in filtered_ami_dict.keys()])
        input_string = f"Select AMI ({ami_options}): "
        ami_choice = input(input_string)
        ami_keys = list(filtered_ami_dict.keys())
        ami_names = [ami[0] for ami in ami_keys]
        if ami_choice in ami_names:
            ami = filtered_ami_dict[ami_keys[ami_names.index(ami_choice)]]
        else:
            print(f"Invalid AMI selection. Defaulting to {ami_keys[0][0]} ({filtered_ami_dict[ami_keys[0]]}).")
            ami = filtered_ami_dict[ami_keys[0]]

        # Prompt user for Instance Type selection
        instance_type = input("Select Instance Type (t3.small, t3.medium): ")
        if instance_type not in ["t3.small", "t3.medium"]:
            print("Invalid Instance Type selection. Defaulting to t3.small.")
            instance_type = "t3.small"

        load_balancer_name = input("Enter Load Balancer Name: ")
        # Store selections as variables
        self.selections = {
            "ami": ami,
            "instance_type": instance_type,
            "region": region,
            "load_balancer_name": load_balancer_name
        }

    def create_terraform_file(self):
        # Terraform Jinja2 template
        terraform_template = """
        provider "aws" {
        region = "{{ region }}"
        }

        resource "aws_instance" "web_server" {
        ami = "{{ ami }}"
        instance_type = "{{ instance_type }}"
        availability_zone = "{{ region }}a"

        tags = {
            Name = "WebServer"
        }
        }

        resource "aws_lb" "application_lb" {
        name = "{{ load_balancer_name }}"
        internal = false
        load_balancer_type = "application"
        security_groups = [aws_security_group.lb_sg.id]
        subnets = aws_subnet.public[*].id
        }

        resource "aws_security_group" "lb_sg" {
        name        = "lb_security_group"
        description = "Allow HTTP inbound traffic"

        ingress {
            from_port   = 80
            to_port     = 80
            protocol    = "tcp"
            cidr_blocks = ["0.0.0.0/0"]
        }
        }

        resource "aws_lb_listener" "http_listener" {
        load_balancer_arn = aws_lb.application_lb.arn
        port              = 80
        protocol          = "HTTP"

        default_action {
            type             = "forward"
            target_group_arn = aws_lb_target_group.web_target_group.arn
        }
        }

        resource "aws_lb_target_group" "web_target_group" {
        name     = "web-target-group"
        port     = 80
        protocol = "HTTP"
        vpc_id   = aws_vpc.main.id
        }

        resource "aws_lb_target_group_attachment" "web_instance_attachment" {
        target_group_arn = aws_lb_target_group.web_target_group.arn
        target_id        = aws_instance.web_server.id
        }

        resource "aws_subnet" "public" {
        count = 2
        vpc_id = aws_vpc.main.id
        cidr_block = "10.0.${count.index}.0/24"
        availability_zone = element(["{{ region }}a", "{{ region }}b"], count.index)
        }

        resource "aws_vpc" "main" {
        cidr_block = "10.0.0.0/16"
        }
        """

        # Render the Terraform template with the user selections
        template = jinja2.Template(terraform_template)
        rendered_template = template.render(self.selections)
        with open("./main.tf", "w") as f:
            f.write(rendered_template)

    def create_terraform(self):
        self.take_input()
        self.create_terraform_file()

if __name__ == "__main__":
    creator = TerraformCreator()
    creator.create_terraform()