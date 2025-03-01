#!/usr/bin/env python3
from aws_cdk import App
from stack import CloudPilotStack

app = App()
CloudPilotStack(app, "CloudPilotTestStack")
app.synth() 