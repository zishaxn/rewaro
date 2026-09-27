import { useState, useEffect } from "react";
import { Amplify, Auth } from "aws-amplify";
import { withAuthenticator, Button, Heading, View, Text } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import awsconfig from "./aws-exports";
import "./App.css";

Amplify.configure(awsconfig);

function App({ signOut, user }) {
  const [loading, setLoading] = useState(false);

  return (
    <View className="app-container">
      <View className="header">
        <Heading level={1}>Rewaro API Manager</Heading>
      </View>
      
      <View className="main-content">
        <View className="user-info">
          <Heading level={2}>Welcome, {user.username}!</Heading>
          <Text>Email: {user.attributes.email}</Text>
          {user.attributes.sub && (
            <Text>User ID: {user.attributes.sub}</Text>
          )}
        </View>

        <Button
          variation="primary"
          onClick={signOut}
          isLoading={loading}
          loadingText="Signing out..."
          className="sign-out-button"
        >
          Sign Out
        </Button>
      </View>
    </View>
  );
}

export default withAuthenticator(App, {
  signUpAttributes: ['email'],
  socialProviders: [],
  variation: "modal",
  hideSignUp: false
});
