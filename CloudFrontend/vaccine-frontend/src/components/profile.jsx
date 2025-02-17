"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useToast } from "@/hooks/use-toast";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { 
  Loader2, 
  Plus, 
  X, 
  User, 
  Mail, 
  Phone, 
  Shield, 
  Key, 
  Calendar,
  Edit,
  Save,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import { commonMedicalConditions, severityOptions } from './constants';
import { MedicalCondition } from './types';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

export function ProfileComponent() {
  const [profile, setProfile] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("personal");
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    user_type: 0,
    identity_type: "",
    identity_number: "",
    phone_number: "",
    medical_conditions: [],
    dob: new Date(),
    public_key: ""
  });

  const API = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get(
          `${API}/api/user/info`,
          {
            params: { token: sessionStorage.access_token }
          }
        );
        setProfile(response.data);
        setFormData(response.data);
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to fetch profile data",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [toast]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    try {
      setIsLoading(true);
      await axios.put(
        `${API}/api/user/update`,
        {
          ...formData,
          token: sessionStorage.access_token
        }
      );
      setProfile(formData);
      setIsEditing(false);
      toast({
        title: "Success",
        description: "Profile updated successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update profile",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-[600px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Profile Header */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5 text-primary" />
                Profile Information
              </CardTitle>
              <CardDescription>
                Manage your personal information and preferences
              </CardDescription>
            </div>
            <Button
              variant={isEditing ? "default" : "outline"}
              onClick={() => setIsEditing(!isEditing)}
              className="gap-2"
            >
              {isEditing ? (
                <>
                  <Save className="h-4 w-4" />
                  Save Changes
                </>
              ) : (
                <>
                  <Edit className="h-4 w-4" />
                  Edit Profile
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="personal">Personal Info</TabsTrigger>
              <TabsTrigger value="medical">Medical History</TabsTrigger>
              <TabsTrigger value="security">Security</TabsTrigger>
            </TabsList>

            <div className="mt-6">
              <AnimatePresence mode="wait" initial={false}>
                {activeTab === "personal" && (
                  <TabsContent value="personal" key="personal-tab" forceMount>
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="space-y-4"
                    >
                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                          <Label htmlFor="first_name">First Name</Label>
                          <Input
                            id="first_name"
                            value={formData.first_name}
                            onChange={(e) => handleInputChange("first_name", e.target.value)}
                            disabled={!isEditing}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="last_name">Last Name</Label>
                          <Input
                            id="last_name"
                            value={formData.last_name}
                            onChange={(e) => handleInputChange("last_name", e.target.value)}
                            disabled={!isEditing}
                          />
                        </div>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                          <Label htmlFor="email">Email</Label>
                          <Input
                            id="email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => handleInputChange("email", e.target.value)}
                            disabled={!isEditing}
                            className="pl-8"
                          />
                          <Mail className="relative -top-[34px] left-2 h-4 w-4 text-muted-foreground" />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="phone">Phone Number</Label>
                          <Input
                            id="phone"
                            value={formData.phone_number}
                            onChange={(e) => handleInputChange("phone_number", e.target.value)}
                            disabled={!isEditing}
                            className="pl-8"
                          />
                          <Phone className="relative -top-[34px] left-2 h-4 w-4 text-muted-foreground" />
                        </div>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                          <Label htmlFor="dob">Date of Birth</Label>
                          <div className="relative">
                            <DatePicker
                              selected={new Date(formData.dob)}
                              onChange={(date) => handleInputChange("dob", date)}
                              disabled={!isEditing}
                              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 pl-8"
                            />
                            <Calendar className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                          </div>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="user_type">User Type</Label>
                          <Select
                            value={formData.user_type.toString()}
                            onValueChange={(value) => handleInputChange("user_type", parseInt(value))}
                            disabled={!isEditing}
                          >
                            <SelectTrigger id="user_type" className="pl-8">
                              <Shield className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                              <SelectValue placeholder="Select user type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="1">Vaccine Recipient</SelectItem>
                              <SelectItem value="2">Healthcare Provider</SelectItem>
                              <SelectItem value="3">Administrator</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </motion.div>
                  </TabsContent>
                )}

                {activeTab === "medical" && (
                  <TabsContent value="medical" key="medical-tab" forceMount>
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="space-y-6"
                    >
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <Label>Medical Conditions</Label>
                          {isEditing && (
                            <Button variant="outline" size="sm" className="gap-2">
                              <Plus className="h-4 w-4" />
                              Add Condition
                            </Button>
                          )}
                        </div>
                        <ScrollArea className="h-[300px] rounded-md border p-4">
                          {formData.medical_conditions?.length > 0 ? (
                            <div className="space-y-4">
                              {formData.medical_conditions.map((condition) => (
                                <Card key={`${condition.name}-${condition.diagnosed_date}`}>
                                  <CardHeader className="pb-2">
                                    <div className="flex items-start justify-between">
                                      <div>
                                        <CardTitle className="text-base">{condition.name}</CardTitle>
                                        <CardDescription>{condition.details}</CardDescription>
                                      </div>
                                      {isEditing && (
                                        <Button variant="ghost" size="icon">
                                          <X className="h-4 w-4" />
                                        </Button>
                                      )}
                                    </div>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="flex items-center gap-2">
                                      <Badge variant="outline">{condition.severity}</Badge>
                                      <Badge variant="secondary">
                                        Diagnosed: {new Date(condition.diagnosed_date).toLocaleDateString()}
                                      </Badge>
                                    </div>
                                  </CardContent>
                                </Card>
                              ))}
                            </div>
                          ) : (
                            <div className="flex flex-col items-center justify-center h-full text-center">
                              <CheckCircle2 className="h-8 w-8 text-success/40" />
                              <h3 className="mt-4 text-lg font-medium">No Medical Conditions</h3>
                              <p className="mt-2 text-sm text-muted-foreground">
                                You haven't added any medical conditions yet
                              </p>
                            </div>
                          )}
                        </ScrollArea>
                      </div>
                    </motion.div>
                  </TabsContent>
                )}

                {activeTab === "security" && (
                  <TabsContent value="security" key="security-tab" forceMount>
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="space-y-6"
                    >
                      <div className="space-y-4">
                        <div className="grid gap-4 md:grid-cols-2">
                          <div className="space-y-2">
                            <Label htmlFor="identity_type">Identity Type</Label>
                            <Select
                              value={formData.identity_type}
                              disabled={true}
                            >
                              <SelectTrigger id="identity_type">
                                <SelectValue placeholder="Select ID type" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="nid">National ID</SelectItem>
                                <SelectItem value="passport">Passport</SelectItem>
                                <SelectItem value="driving_license">Driving License</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="identity_number">Identity Number</Label>
                            <Input
                              id="identity_number"
                              value={formData.identity_number}
                              disabled={true}
                              className="bg-muted"
                            />
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="public_key">Public Key</Label>
                          <div className="relative">
                            <Input
                              id="public_key"
                              value={formData.public_key}
                              disabled
                              className="pr-24 font-mono text-sm bg-muted"
                            />
                            <Button
                              variant="ghost"
                              size="sm"
                              className="absolute right-2 top-1"
                              onClick={() => {
                                navigator.clipboard.writeText(formData.public_key);
                                toast({
                                  title: "Copied",
                                  description: "Public key copied to clipboard",
                                });
                              }}
                            >
                              Copy
                            </Button>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            This is your unique public key used for vaccine verification
                          </p>
                        </div>

                        <Card className="border-destructive/50 bg-destructive/5">
                          <CardHeader>
                            <CardTitle className="text-base flex items-center gap-2 text-destructive">
                              <AlertTriangle className="h-5 w-5" />
                              Danger Zone
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <h4 className="font-medium">Delete Account</h4>
                                <p className="text-sm text-muted-foreground">
                                  Permanently delete your account and all associated data
                                </p>
                              </div>
                              <Button variant="destructive" size="sm">
                                Delete Account
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </motion.div>
                  </TabsContent>
                )}
              </AnimatePresence>
            </div>
          </Tabs>
        </CardContent>
        {isEditing && (
          <CardFooter className="flex justify-end space-x-4 pt-6">
            <Button
              variant="outline"
              onClick={() => {
                setFormData(profile);
                setIsEditing(false);
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </Button>
          </CardFooter>
        )}
      </Card>
    </motion.div>
  );
}
