from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3
)
from constructs import Construct

class CloudPilotStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "cloudpilot_vpc",
            max_azs=2
        )

        # Security group
        security_group = ec2.SecurityGroup(self, "cloudpilot_sg",
            vpc=vpc,
            allow_all_outbound=True,
            description="Allow HTTP traffic"
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
            "Allow HTTP traffic"
        )

        # EC2 instance
        instance = ec2.Instance(self, "cloudpilot_instance",
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            machine_image=ec2.MachineImage.generic_linux({
                "us-east-1": "ami-0c7217cdde317cfec"
            }),
            vpc=vpc,
            security_group=security_group
        )

        # S3 bucket for static files
        bucket = s3.Bucket(self, "cloudpilot_bucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )