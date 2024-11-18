"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { motion } from "framer-motion";
import axios from "axios";

export function ProfileComponent() {
  const [profile, setProfile] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      const postData = {
        token: sessionStorage.access_token,
      };

      const response = await axios.post(
        "http://localhost:8000/user-info",
        postData
      );

      setProfile(response.data);
    };

    fetchProfile();
  }, []);

  const handleEdit = () => {
    setIsEditing(!isEditing);
  };

  const handleSave = () => {
    // Placeholder for Axios data updating
    setIsEditing(false);
  };

  if (!profile) {
    return <div>Loading...</div>;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="first_name">First Name</Label>
              <Input
                id="first_name"
                defaultValue={profile.first_name}
                disabled={!isEditing}
              />
            </div>

            <div>
              <Label htmlFor="last_name">Last Name</Label>
              <Input
                id="last_name"
                defaultValue={profile.last_name}
                disabled={!isEditing}
              />
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                defaultValue={profile.email}
                disabled={!isEditing}
              />
            </div>

            <div>
              <Label htmlFor="dob">Date of Birth</Label>
              <Input
                id="dob"
                type="date"
                defaultValue={profile.dob}
                disabled={!isEditing}
              />
            </div>

            <div>
              <Label htmlFor="address">National ID</Label>
              <Input
                id="address"
                defaultValue={profile.national_id}
                disabled={!isEditing}
              />
            </div>
            
          </div>
          <div className="flex justify-end space-x-2">
            <Button onClick={handleEdit}>
              {isEditing ? "Cancel" : "Edit"}
            </Button>
            {isEditing && (
              <Button
                onClick={handleSave}
                className="bg-green-500 hover:bg-green-600"
              >
                Save
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
