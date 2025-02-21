from python_terraform import Terraform, IsFlagged, IsNotFlagged

class TerraformRunner:
    def __init__(self, working_dir='.'):
        self.tf = Terraform(working_dir=working_dir)

    def run_init(self):
        print("Running 'terraform init'...")
        return_code, stdout, stderr = self.tf.init()
        if return_code != 0:
            print(f"Error during 'terraform init': {stderr}")
            return False
        return True

    def run_plan(self):
        print("Running 'terraform plan'...")
        return_code, stdout, stderr = self.tf.plan(out='plan.out')
        if return_code != 0:
            print(f"Error during 'terraform plan': {stderr}")
            return False
        return True

    def run_apply(self):
        print("Running 'terraform apply'...")
        return_code, stdout, stderr = self.tf.apply('plan.out', skip_plan=True)
        if return_code != 0:
            print(f"Error during 'terraform apply': {stderr}")
            return False
        return True

    def capture_output(self):
        print("Capturing Terraform output...")
        return_code, stdout, stderr = self.tf.output()
        if return_code == 0:
            instance_id = self.tf.output('aws_instance.web_server.id')[1]
            lb_dns_name = self.tf.output('aws_lb.application_lb.dns_name')[1]
            print(f"Instance ID: {instance_id}")
            print(f"Load Balancer DNS Name: {lb_dns_name}")
            return (instance_id, lb_dns_name)
        else:
            print(f"Error during 'terraform output': {stderr}")
            return None

    def run(self):
        try:
            if not self.run_init():
                return
            if not self.run_plan():
                return
            if not self.run_apply():
                return
            self.capture_output()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    runner = TerraformRunner()
    runner.run()