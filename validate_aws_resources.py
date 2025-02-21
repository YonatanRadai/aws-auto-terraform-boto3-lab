import boto3
import json

class AWSResourceValidator:
    def __init__(self, instance_id="i-0afbb2ca7b05cf032", alb_name='dan-lb-exam'):
        self.instance_id = instance_id
        self.alb_name = alb_name

    def fetch_instance_details(self):
        ec2 = boto3.client('ec2')
        try:
            response = ec2.describe_instances(InstanceIds=[self.instance_id])
            if not response['Reservations']:
                raise ValueError(f"No reservations found for instance ID {self.instance_id}")
            instance = response['Reservations'][0]['Instances'][0]
            instance_state = instance['State']['Name']
            public_ip = instance.get('PublicIpAddress', 'N/A')
            return instance_state, public_ip
        except Exception as e:
            print(f"Error fetching instance details: {e}")
            return None, None

    def fetch_alb_details(self):
        elbv2 = boto3.client('elbv2')
        try:
            response = elbv2.describe_load_balancers(Names=[self.alb_name])
            if not response['LoadBalancers']:
                raise ValueError(f"No load balancers found with name {self.alb_name}")
            load_balancer = response['LoadBalancers'][0]
            alb_dns_name = load_balancer['DNSName']
            return alb_dns_name
        except Exception as e:
            print(f"Error fetching ALB details: {e}")
            return None

    def validate_aws_resources(self):
        # Fetch instance details
        instance_state, public_ip = self.fetch_instance_details()
        if instance_state is None or public_ip is None:
            print("Failed to fetch instance details.")
            return

        # Fetch ALB details
        alb_dns_name = self.fetch_alb_details()
        if alb_dns_name is None:
            print("Failed to fetch ALB details.")
            return

        # Store the verification data as a JSON file
        verification_data = {
            "instance_id": self.instance_id,
            "instance_state": instance_state,
            "public_ip": public_ip,
            "load_balancer_dns": alb_dns_name
        }

        with open("aws_validation.json", "w") as json_file:
            json.dump(verification_data, json_file, indent=4)

        print("Verification data saved to aws_validation.json")

if __name__ == "__main__":
    validator = AWSResourceValidator()
    validator.validate_aws_resources()