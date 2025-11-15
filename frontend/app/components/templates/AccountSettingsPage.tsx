"use client";

import React from "react";
import UserProfileCard from "../dashboard/UserProfileCard";

interface DashboardUser {
  id: number;
  username: string;
  email: string;
  hasXCredentials?: boolean;
  createdAt?: string;
}

interface AccountSettingsPageProps {
  user: DashboardUser | null;
  onLogout: () => Promise<void>;
  onCredentialsChange: (hasKeys: boolean) => void;
}

const AccountSettingsPage: React.FC<AccountSettingsPageProps> = ({
  user,
  onLogout,
  onCredentialsChange,
}) => {
  if (!user) {
    return (
      <div className="p-6 text-center text-gray-300">
        <p>Loading account details...</p>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 space-y-4">
      <h1 className="text-2xl font-semibold text-white">Account & X API Keys</h1>
      <p className="text-sm text-gray-400">
        Manage your dashboard session, update encrypted X publishing keys, and control logout.
      </p>
      <UserProfileCard
        user={user}
        onLogout={onLogout}
        onCredentialsChange={onCredentialsChange}
      />
    </div>
  );
};

export default AccountSettingsPage;
