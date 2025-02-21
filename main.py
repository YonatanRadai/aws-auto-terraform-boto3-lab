import jinja2
from create_terraform import TerraformCreator
from run_terraform import TerraformRunner
from validate_aws_resources import AWSResourceValidator

def main():
    # Create Terraform configuration
    creator = TerraformCreator()
    creator.create_terraform()

    # Run Terraform commands
    runner = TerraformRunner()
    result = runner.run()

    # Validate AWS resources
    if result is None:
        validator = AWSResourceValidator()
        validator.validate_aws_resources()
    else:
        instance_id, lb_dns_name = result
        validator = AWSResourceValidator(instance_id, lb_dns_name)
        validator.validate_aws_resources()

if __name__ == "__main__":
    main()