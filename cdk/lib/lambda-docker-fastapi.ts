import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import { aws_lambda as lambda } from "aws-cdk-lib";
import * as path from "path";
import { Architecture } from "aws-cdk-lib/aws-lambda";

export class CdkLambdaDockerFastapiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new lambda.DockerImageFunction(this, "LambdaFunction_1", {
      code: lambda.DockerImageCode.fromImageAsset(
        path.join(__dirname, "../../python"),
        {
          cmd: ["main.handler"],
        }
      ),
      architecture: Architecture.X86_64,
    });
  }
}