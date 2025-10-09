import { ResourcesConfig } from "aws-amplify";

const awsExports: ResourcesConfig = {
  Auth: {
    Cognito: {
      userPoolId: "your-user-pool-id",
      userPoolClientId: "your-user-pool-client-id",
      identityPoolId: "your-identity-pool-id",
      loginWith: {
        username: true, // or email: true
      },
    },
  },
};

export default awsExports;