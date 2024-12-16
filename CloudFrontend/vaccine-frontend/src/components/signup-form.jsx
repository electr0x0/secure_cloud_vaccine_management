'use client'

import { useState } from 'react'
import { useForm, Controller, setError } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Loader2, X, Plus } from 'lucide-react'
import { useToast } from "@/hooks/use-toast"
import { registerUser } from './api'
import DatePicker from "react-datepicker"
import "react-datepicker/dist/react-datepicker.css"
import { commonMedicalConditions, severityOptions, userTypes, identityValidationPatterns } from './constants'
import { Card, CardContent } from "@/components/ui/card"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

const signupSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email address"),
  user_type: z.enum(["1", "2"]),
  identity_type: z.enum(["nid", "brn", "passport"]),
  identity_number: z.string(),
  phone_number: z.string().regex(/^\d+$/, "Phone number must contain only digits"),
  medical_conditions: z.array(z.object({
    condition_name: z.string(),
    details: z.string(),
    severity: z.string(),
    diagnosed_date: z.string()
  })),
  dob: z.date().transform(date => date.toISOString().split('T')[0]), // Transform to YYYY-MM-DD format
  password: z.string().min(8, "Password must be at least 8 characters long"),
  terms: z.literal(true, {
    errorMap: () => ({ message: "You must agree to the terms and conditions" })
  })
})

const validateIdentityNumber = (identityType, number) => {
  const pattern = identityValidationPatterns[identityType];
  if (!pattern || !pattern.test(number)) {
    return `Invalid ${identityType.toUpperCase()} number format`;
  }
  return null;
};

export default function SignupForm() {
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()
  const { control, handleSubmit, watch, setValue, formState: { errors }, setError } = useForm({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      user_type: "1",
      identity_type: "nid",
      identity_number: "",
      phone_number: "",
      dob: null,
      password: "",
      terms: false,
      medical_conditions: []
    }
  })

  const identityType = watch('identity_type')

  const onSubmit = async (data) => {
    setIsLoading(true);
    const identityError = validateIdentityNumber(data.identity_type, data.identity_number);
    if (identityError) {
      setError('identity_number', { type: 'manual', message: identityError });
      setIsLoading(false);
      return;
    }
    try {
      const result = await registerUser(data)
      if (result.success) {
        toast({
          title: "Success",
          description: "Your account has been created successfully",
        })
      }
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "An error occurred during registration",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const addMedicalCondition = (condition) => {
    const currentConditions = watch('medical_conditions')
    setValue('medical_conditions', [...currentConditions, {
      condition_name: condition.label,
      details: "",
      severity: "moderate",
      diagnosed_date: new Date().toISOString().split('T')[0]
    }])
  }

  const removeMedicalCondition = (index) => {
    const currentConditions = watch('medical_conditions')
    setValue('medical_conditions', currentConditions.filter((_, i) => i !== index))
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="first_name">First Name</Label>
          <Controller
            name="first_name"
            control={control}
            render={({ field }) => <Input {...field} />}
          />
          {errors.first_name && <p className="text-sm text-red-500">{errors.first_name.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="last_name">Last Name</Label>
          <Controller
            name="last_name"
            control={control}
            render={({ field }) => <Input {...field} />}
          />
          {errors.last_name && <p className="text-sm text-red-500">{errors.last_name.message}</p>}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Controller
          name="email"
          control={control}
          render={({ field }) => <Input {...field} type="email" />}
        />
        {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="user_type">User Type</Label>
        <Controller
          name="user_type"
          control={control}
          render={({ field }) => (
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <SelectTrigger>
                <SelectValue placeholder="Select user type" />
              </SelectTrigger>
              <SelectContent>
                {userTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />
        {errors.user_type && <p className="text-sm text-red-500">{errors.user_type.message}</p>}
      </div>

      <div className="space-y-2">
        <Label>Identity Type</Label>
        <Controller
          name="identity_type"
          control={control}
          render={({ field }) => (
            <RadioGroup
              onValueChange={field.onChange}
              defaultValue={field.value}
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
          )}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="identity_number">
          {identityType === 'nid' ? 'National ID Number' :
           identityType === 'brn' ? 'Birth Registration Number' :
           'Passport Number'}
        </Label>
        <Controller
          name="identity_number"
          control={control}
          render={({ field }) => <Input {...field} />}
        />
        {errors.identity_number && <p className="text-sm text-red-500">{errors.identity_number.message}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="phone_number">Phone Number</Label>
        <Controller
          name="phone_number"
          control={control}
          render={({ field }) => <Input {...field} type="tel" />}
        />
        {errors.phone_number && <p className="text-sm text-red-500">{errors.phone_number.message}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="dob">Date of Birth</Label>
        <Controller
          name="dob"
          control={control}
          render={({ field }) => (
            <DatePicker
              selected={field.value}
              onChange={(date) => field.onChange(date)}
              dateFormat="yyyy-MM-dd"
              maxDate={new Date()}
              showYearDropdown
              scrollableYearDropdown
              yearDropdownItemNumber={100}
              placeholderText="Select Date of Birth"
              customInput={<Input />}
              isClearable
            />
          )}
        />
        {errors.dob && <p className="text-sm text-red-500">{errors.dob.message}</p>}
      </div>

      <div className="space-y-2">
        <Label>Medical Conditions</Label>
        <Controller
          name="medical_conditions"
          control={control}
          render={({ field }) => (
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2">
                {field.value.map((condition, index) => (
                  <Badge key={index} variant="secondary">
                    {condition.condition_name} ({condition.severity})
                    <button
                      type="button"
                      onClick={() => removeMedicalCondition(index)}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
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
            </div>
          )}
        />
      </div>

      {watch('medical_conditions').map((condition, index) => (
        <Card key={index}>
          <CardContent className="pt-6">
            <div className="space-y-2">
              <Label>Condition Details</Label>
              <Textarea
                value={condition.details}
                onChange={(e) => {
                  const updatedConditions = [...watch('medical_conditions')]
                  updatedConditions[index].details = e.target.value
                  setValue('medical_conditions', updatedConditions)
                }}
                placeholder="Enter condition details"
              />
            </div>
            <div className="space-y-2 mt-2">
              <Label>Severity</Label>
              <Select
                value={condition.severity}
                onValueChange={(value) => {
                  const updatedConditions = [...watch('medical_conditions')]
                  updatedConditions[index].severity = value
                  setValue('medical_conditions', updatedConditions)
                }}
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
                onChange={(date) => {
                  const updatedConditions = [...watch('medical_conditions')]
                  updatedConditions[index].diagnosed_date = date.toISOString().split('T')[0]
                  setValue('medical_conditions', updatedConditions)
                }}
                dateFormat="yyyy-MM-dd"
                maxDate={new Date()}
                customInput={<Input />}
              />
            </div>
          </CardContent>
        </Card>
      ))}

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Controller
          name="password"
          control={control}
          render={({ field }) => <Input {...field} type="password" />}
        />
        {errors.password && <p className="text-sm text-red-500">{errors.password.message}</p>}
      </div>

      <div className="flex items-center space-x-2">
        <Controller
          name="terms"
          control={control}
          render={({ field }) => (
            <Checkbox 
              checked={field.value}
              onCheckedChange={field.onChange}
              id="terms"
            />
          )}
        />
        <Label htmlFor="terms" className="text-sm">
          I agree to the terms and conditions
        </Label>
      </div>
      {errors.terms && <p className="text-sm text-red-500">{errors.terms.message}</p>}

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Signing up...
          </>
        ) : (
          "Sign Up"
        )}
      </Button>
    </form>
  )
}
