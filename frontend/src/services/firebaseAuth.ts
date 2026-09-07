import {
    GoogleAuthProvider,
    createUserWithEmailAndPassword,
    onIdTokenChanged,
    sendEmailVerification,
    signInWithEmailAndPassword,
    signInWithPopup,
    signOut,
    type User,
} from "firebase/auth";

import { firebaseAuth, firebaseConfigured } from "../config/firebase";

function configuredAuth() {
    if (!firebaseAuth) throw new Error("Firebase authentication is not configured.");
    return firebaseAuth;
}

export async function firebaseEmailLogin(email: string, password: string): Promise<User> {
    return (await signInWithEmailAndPassword(configuredAuth(), email, password)).user;
}

export async function firebaseEmailRegister(email: string, password: string): Promise<void> {
    const credential = await createUserWithEmailAndPassword(configuredAuth(), email, password);
    await sendEmailVerification(credential.user);
    await signOut(configuredAuth());
}

export async function firebaseGoogleLogin(): Promise<User> {
    const provider = new GoogleAuthProvider();
    provider.setCustomParameters({ prompt: "select_account" });
    return (await signInWithPopup(configuredAuth(), provider)).user;
}

export async function firebaseLogout(): Promise<void> {
    if (firebaseAuth) await signOut(firebaseAuth);
}

export async function restoredFirebaseUser(): Promise<User | null> {
    if (!firebaseAuth) return null;
    await firebaseAuth.authStateReady();
    return firebaseAuth.currentUser;
}

export function observeFirebaseToken(callback: (user: User | null) => void): () => void {
    return firebaseAuth ? onIdTokenChanged(firebaseAuth, callback) : () => undefined;
}

export { firebaseConfigured };
