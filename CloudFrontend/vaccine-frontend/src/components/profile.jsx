"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useToast } from "@/hooks/use-toast";
import axios from "axios";
import { Loader2, Plus, X } from 'lucide-react';
import { commonMedicalConditions, severityOptions } from './constants';
import { MedicalCondition } from './types';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

export function ProfileComponent() {
  const [profile, setProfile] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    user_type: 0,
    identity_type: "",
    identity_number: "",
    phone_number: "",
    medical_conditions: [], // Initialize as empty array
    dob: new Date(),
    public_key: ""
  });

  const API = process.env.NEXT_PUBLIC_API_URL

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(
          `${API}/api/user/info`,
          {
            params: { token: sessionStorage.access_token }
          }
        );

        // Parse medical_conditions if it's a string
        let parsedMedicalConditions = [];
        if (typeof response.data.medical_conditions === 'string') {
          try {
            parsedMedicalConditions = JSON.parse(response.data.medical_conditions);
          } catch (e) {
            console.error('Error parsing medical conditions:', e);
            parsedMedicalConditions = [];
          }
        } else if (Array.isArray(response.data.medical_conditions)) {
          parsedMedicalConditions = response.data.medical_conditions;
        }

        setProfile(response.data);
        setFormData({
          ...response.data,
          dob: response.data.dob ? new Date(response.data.dob) : new Date(),
          medical_conditions: parsedMedicalConditions || [] // Ensure it's an array
        });
      } catch (error) {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to fetch profile information"
        });
      }
    };

    fetchProfile();
  }, []);

  const handleEdit = () => {
    if (isEditing) {
      // Reset form data when canceling
      let parsedMedicalConditions = [];
      if (typeof profile.medical_conditions === 'string') {
        try {
          parsedMedicalConditions = JSON.parse(profile.medical_conditions);
        } catch (e) {
          console.error('Error parsing medical conditions:', e);
          parsedMedicalConditions = [];
        }
      } else if (Array.isArray(profile.medical_conditions)) {
        parsedMedicalConditions = profile.medical_conditions;
      }

      setFormData({
        ...profile,
        dob: new Date(profile.dob),
        medical_conditions: parsedMedicalConditions || [] // Ensure it's an array
      });
    }
    setIsEditing(!isEditing);
  };

  const handleInputChange = (e) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id]: value,
    }));
  };

  const handleIdentityTypeChange = (value) => {
    setFormData((prev) => ({
      ...prev,
      identity_type: value
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      const updateData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        identity_type: formData.identity_type,
        identity_number: formData.identity_number,
        phone_number: formData.phone_number,
        medical_conditions: formData.medical_conditions || [], // Ensure it's an array
        dob: formData.dob instanceof Date 
          ? formData.dob.toISOString().split('T')[0]
          : formData.dob,
        token: sessionStorage.access_token,
      };

      const response = await axios.put(
        `${API}/api/user/update`,
        updateData
      );

      setProfile(response.data);
      setIsEditing(false);
      toast({
        title: "Success",
        description: "Profile updated successfully",
      });
    } catch (error) {
      // Improved error handling
      let errorMessage = "Failed to update profile";
      
      if (error.response?.data) {
        if (typeof error.response.data === 'object') {
          errorMessage = error.response.data.detail || 
                        Object.values(error.response.data)[0] ||
                        errorMessage;
        } else {
          errorMessage = error.response.data;
        }
      }

      toast({
        variant: "destructive",
        title: "Error",
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const addMedicalCondition = (condition) => {
    setFormData((prev) => ({
      ...prev,
      medical_conditions: [
        ...(Array.isArray(prev.medical_conditions) ? prev.medical_conditions : []),
        {
          condition_name: condition.label,
          details: "",
          severity: "moderate",
          diagnosed_date: new Date().toISOString().split('T')[0]
        }
      ]
    }));
  };

  const removeMedicalCondition = (index) => {
    setFormData((prev) => ({
      ...prev,
      medical_conditions: Array.isArray(prev.medical_conditions) 
        ? prev.medical_conditions.filter((_, i) => i !== index)
        : []
    }));
  };

  const updateMedicalCondition = (index, field, value) => {
    setFormData((prev) => {
      const conditions = Array.isArray(prev.medical_conditions) 
        ? [...prev.medical_conditions]
        : [];
      if (conditions[index]) {
        conditions[index] = {
          ...conditions[index],
          [field]: value
        };
      }
      return {
        ...prev,
        medical_conditions: conditions
      };
    });
  };

  if (!profile) {
    return <div>Loading...</div>;
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Profile Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="first_name">First Name</Label>
            <Input
              id="first_name"
              value={formData.first_name}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="last_name">Last Name</Label>
            <Input
              id="last_name"
              value={formData.last_name}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              disabled={true}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="dob">Date of Birth</Label>
            <DatePicker
              selected={formData.dob instanceof Date ? formData.dob : new Date(formData.dob)}
              onChange={(date) => setFormData(prev => ({ ...prev, dob: date }))}
              dateFormat="yyyy-MM-dd"
              maxDate={new Date()}
              showYearDropdown
              scrollableYearDropdown
              yearDropdownItemNumber={100}
              disabled={!isEditing}
              customInput={<Input />}
            />
          </div>

          <div className="space-y-2">
            <Label>Identity Type</Label>
            <RadioGroup
              value={formData.identity_type}
              onValueChange={handleIdentityTypeChange}
              disabled={!isEditing}
              className="flex space-x-4"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="nid" id="nid" />
                <Label htmlFor="nid">National ID</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="brn" id="brn" />
                <Label htmlFor="brn">Birth Registration</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="passport" id="passport" />
                <Label htmlFor="passport">Passport</Label>
              </div>
            </RadioGroup>
          </div>

          <div className="space-y-2">
            <Label htmlFor="identity_number">Identity Number</Label>
            <Input
              id="identity_number"
              value={formData.identity_number}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone_number">Phone Number</Label>
            <Input
              id="phone_number"
              value={formData.phone_number}
              onChange={handleInputChange}
              disabled={!isEditing}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="user_type">User Type</Label>
            <Input
              id="user_type"
              value={formData.user_type === 1 ? "Vaccine Recipient" : "Vaccinator"}
              disabled={true}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label>Medical Conditions</Label>
          <div className="flex flex-wrap gap-2 mb-2">
            {Array.isArray(formData.medical_conditions) && formData.medical_conditions.map((condition, index) => (
              <Badge key={index} variant="secondary">
                {condition.condition_name} ({condition.severity})
                {isEditing && (
                  <button
                    type="button"
                    onClick={() => removeMedicalCondition(index)}
                    className="ml-1 hover:text-destructive"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </Badge>
            ))}
          </div>
          {isEditing && (
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-full justify-start">
                  <Plus className="mr-2 h-4 w-4" /> Add Medical Condition
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-80">
                <div className="grid gap-4">
                  <h4 className="font-medium leading-none">Add Medical Condition</h4>
                  <div className="grid gap-2">
                    {commonMedicalConditions.map((condition) => (
                      <Button
                        key={condition.value}
                        variant="ghost"
                        className="justify-start"
                        onClick={() => addMedicalCondition(condition)}
                      >
                        {condition.label}
                      </Button>
                    ))}
                  </div>
                </div>
              </PopoverContent>
            </Popover>
          )}
        </div>

        {Array.isArray(formData.medical_conditions) && formData.medical_conditions.map((condition, index) => (
          <Card key={index}>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <Label>Condition Details</Label>
                <Textarea
                  value={condition.details}
                  onChange={(e) => updateMedicalCondition(index, 'details', e.target.value)}
                  placeholder="Enter condition details"
                  disabled={!isEditing}
                />
              </div>
              <div className="space-y-2 mt-2">
                <Label>Severity</Label>
                <Select
                  value={condition.severity}
                  onValueChange={(value) => updateMedicalCondition(index, 'severity', value)}
                  disabled={!isEditing}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select severity" />
                  </SelectTrigger>
                  <SelectContent>
                    {severityOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2 mt-2">
                <Label>Diagnosed Date</Label>
                <DatePicker
                  selected={new Date(condition.diagnosed_date)}
                  onChange={(date) => updateMedicalCondition(index, 'diagnosed_date', date.toISOString().split('T')[0])}
                  dateFormat="yyyy-MM-dd"
                  maxDate={new Date()}
                  disabled={!isEditing}
                  customInput={<Input />}
                />
              </div>
            </CardContent>
          </Card>
        ))}

        <div className="flex justify-end space-x-2">
          <Button onClick={handleEdit} disabled={isLoading}>
            {isEditing ? "Cancel" : "Edit"}
          </Button>
          {isEditing && (
            <Button
              onClick={handleSave}
              className="bg-green-500 hover:bg-green-600"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save"
              )}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
