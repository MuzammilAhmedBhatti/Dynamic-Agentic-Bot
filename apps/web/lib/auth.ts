export type AuthenticationState = "not-connected" | "authenticated" | "unauthenticated";

export interface AuthenticatedPrincipal {
  userId: string;
  organizationId: string;
}

export interface AuthenticationBoundary {
  state: AuthenticationState;
  principal: AuthenticatedPrincipal | null;
}

export const phaseOneAuthenticationBoundary: AuthenticationBoundary = {
  state: "not-connected",
  principal: null,
};
