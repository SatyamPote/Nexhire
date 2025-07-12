// static/js/firebase_google_login.js

// Import the functions you need from the SDKs you want to use
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, GoogleAuthProvider, signInWithPopup, signInWithRedirect, onAuthStateChanged, getIdToken } from "firebase/auth";

// Your web app's Firebase configuration
// Ensure these are loaded securely, e.g., from a config file or environment variable on the frontend
const firebaseConfig = {
  apiKey: "AIzaSyDr0uUFPfHDGo3iHGNAyPDu9xX1s9VYaJw", // <<< Replace with your actual Firebase Web API Key
  authDomain: "nexhire-8431.firebaseapp.com",
  projectId: "nexhire-8431",
  storageBucket: "nexhire-8431.firebasestorage.app",
  messagingSenderId: "291151525916",
  appId: "1:291151525916:web:ff23b7c2ef99c237da07d9",
  measurementId: "G-MQKM2JNJYR"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app); // Only if you need analytics

const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// Function to initiate Google Sign-In
function signInWithGoogle() {
    signInWithPopup(auth, provider)
        .then((result) => {
            // This gives you a Google User object and the Google ID token.
            const credential = GoogleAuthProvider.credentialFromResult(result);
            const token = credential.accessToken; // Access token to the Google API
            const user = result.user; // Google User object
            const googleIdToken = result.user.getIdToken(); // Get the Firebase ID Token

            console.log("Firebase User:", user);
            console.log("Firebase ID Token:", googleIdToken);

            // Now, send this Firebase ID token to your Django backend for verification
            sendFirebaseTokenToBackend(googleIdToken);
        })
        .catch((error) => {
            // Handle errors here.
            const errorCode = error.code;
            const errorMessage = error.message;
            console.error("Google Sign-In Error:", errorCode, errorMessage);
            alert("Could not sign in with Google. Please try again.");
        });
}

// Function to send the Firebase ID Token to your Django backend
async function sendFirebaseTokenToBackend(idToken) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')[0].value; // Get CSRF token from cookies or hidden input

    try {
        const response = await fetch('/verify-firebase-token/', { // Your Django endpoint to verify token
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Include CSRF token for security
            },
            body: JSON.stringify({ idToken: idToken }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
            console.log("Backend verification successful:", data.message);
            // Redirect user to dashboard or intended page after successful login
            window.location.href = '/'; // Or wherever LOGIN_REDIRECT_URL points
        } else {
            console.error("Backend verification failed:", data.error);
            alert(`Login failed: ${data.error}`);
        }
    } catch (error) {
        console.error("Error sending token to backend:", error);
        alert("An error occurred during login. Please try again.");
    }
}

// --- Add event listener for the Google Sign-In button ---
// You'll need a button in your HTML with an ID like 'google-signin-button'
document.addEventListener('DOMContentLoaded', (event) => {
    const googleButton = document.getElementById('google-signin-button');
    if (googleButton) {
        googleButton.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent default link behavior
            signInWithGoogle();
        });
    }
});

// Optional: Listen for authentication state changes
// onAuthStateChanged(auth, (user) => {
//     if (user) {
//         // User is signed in.
//         console.log("User is signed in with Firebase:", user.displayName, user.email);
//         // You might want to re-verify token or ensure Django session is active
//     } else {
//         // User is signed out.
//         console.log("User is signed out.");
//         // Potentially redirect to login or handle sign-out from Django's side
//     }
// });