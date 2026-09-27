import React from "react";
import { Amplify } from "aws-amplify";
import { Authenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import awsExports from "./prod-exports";
Amplify.configure(awsExports);

const signUpConfig = {
  hideAllDefaults: true,
  signUpFields: [
    {
      label: "Phone Number",
      key: "phone_number",
      required: true,
      type: "tel",
      placeholder: "Enter your phone number",
    },
    {
      label: "Password",
      key: "password",
      required: true,
      type: "password",
      placeholder: "Enter your password",
    },
  ],
};

export default function App() {
  return (
    <Authenticator
      initialState="signUp"
      signUpConfig={signUpConfig}
      loginMechanisms={["phone_number"]}
    >
      {({ signOut, user }) => (
        <main>
          <h1>Hello {user.username}</h1>
          <button onClick={signOut}>Sign out</button>
        </main>
      )}
    </Authenticator>
  );
}
