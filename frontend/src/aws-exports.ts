import { ResourcesConfig } from "aws-amplify";

const awsExports: ResourcesConfig = {
  Auth: {
    Cognito: {
      userPoolId: process.env.REACT_APP_USER_POOL_ID || "",
      userPoolClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID || "",
      identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID || "",
      loginWith: {
        email: true,
      },
    },
  },
};

export default awsExports;
