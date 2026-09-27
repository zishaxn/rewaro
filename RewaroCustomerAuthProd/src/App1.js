import React from "react";
import { Amplify } from "aws-amplify";
import { Authenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import awsExports from "./aws-exports";
Amplify.configure(awsExports);

export default function App() {
  return (
    <Authenticator
      loginMechanisms={['phone_number']}
      signUpAttributes={['phone_number']}
      formFields={{
        signUp: {
          phone_number: {
            label: 'Phone Number',
            placeholder: 'Enter your phone number',
            required: true,
            type: 'tel',
          },
          password: {
            label: 'Password',
            placeholder: 'Enter your password',
            required: true,
            type: 'password',
          },
        },
      }}
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
