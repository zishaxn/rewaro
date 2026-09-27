import React from "react";
import { Amplify } from "aws-amplify";
import {
  Authenticator,
  useTheme,
  View,
  Text,
  Heading,
  useAuthenticator,
} from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import awsExports from "./aws-exports";

Amplify.configure(awsExports);

// Custom components for Authenticator
const components = {
  Header() {
    const { tokens } = useTheme();

    return (
      <View textAlign="center" padding={tokens.space.large}>
        <Heading level={3}>Welcome</Heading>
      </View>
    );
  },

  Footer() {
    const { tokens } = useTheme();
    return (
      <View textAlign="center" padding={tokens.space.small}>
        <Text
          color={tokens.colors.neutral[80]}
          fontSize={tokens.fontSizes.small}
        >
          By continuing, you agree to our terms of service
        </Text>
      </View>
    );
  },

  ConfirmSignIn: {
    Header() {
      return (
        <Heading padding="1rem" textAlign="center" level={3}>
          Enter Verification Code
        </Heading>
      );
    },
    Footer() {
      return (
        <Text
          padding="0.5rem"
          textAlign="center"
          color="gray.500"
          fontSize="sm"
        >
          Please enter the code sent to your phone
        </Text>
      );
    },
  },
};

// Separate component for authenticated state
const AuthenticatedContent = ({ user, signOut }) => {
  React.useEffect(() => {
    const checkSession = async () => {
      try {
        await Amplify.Auth.currentSession();
      } catch (error) {
        signOut();
      }
    };

    checkSession();
    const interval = setInterval(checkSession, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [signOut]);

  return (
    <View padding="2rem">
      <View
        backgroundColor="white"
        padding="2rem"
        borderRadius="medium"
        boxShadow="small"
      >
        <Heading level={2} marginBottom="1rem">
          Welcome back, {user.attributes?.phone_number}
        </Heading>

        <Text marginBottom="2rem">
          You're successfully authenticated with MFA.
        </Text>

        <button
          onClick={signOut}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#FF4B4B",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "1rem",
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#E43E3E")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#FF4B4B")}
        >
          Sign Out
        </button>
      </View>
    </View>
  );
};

export default function App() {
  return (
    <Authenticator
      loginMechanisms={["phone_number"]}
      signUpAttributes={["phone_number"]}
      components={components}
      services={{
        async validateCustomSignUp(formData) {
          if (!formData.phone_number) {
            return {
              phone_number: "Phone number is required",
            };
          }
          return {};
        },
        async validateCustomSignIn(formData) {
          if (!formData.phone_number) {
            return {
              phone_number: "Phone number is required",
            };
          }
          return {};
        },
      }}
      formFields={{
        signUp: {
          phone_number: {
            label: "Phone Number",
            placeholder: "+1 (555) 555-5555",
            required: true,
            order: 1,
            type: "tel",
          },
          password: {
            label: "Password",
            placeholder: "Create a password",
            required: true,
            order: 2,
          },
        },
        signIn: {
          phone_number: {
            label: "Phone Number",
            placeholder: "+1 (555) 555-5555",
            required: true,
            order: 1,
            type: "tel",
          },
          password: {
            label: "Password",
            placeholder: "Enter your password",
            required: true,
            order: 2,
          },
        },
        confirmSignIn: {
          confirmation_code: {
            label: "Verification Code",
            placeholder: "Enter code",
            required: true,
          },
        },
        confirmSignUp: {
          confirmation_code: {
            label: "Verification Code",
            placeholder: "Enter the code sent to your phone",
            required: true,
          },
        },
        setupMFA: {
          confirmation_code: {
            label: "Verification Code",
            placeholder: "Enter the code sent to your phone",
            required: true,
          },
        },
      }}
    >
      {({ signOut, user }) => (
        <AuthenticatedContent user={user} signOut={signOut} />
      )}
    </Authenticator>
  );
}
