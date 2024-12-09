import React from 'react'
import { Document, Page, Text, View, StyleSheet, Image, Font } from '@react-pdf/renderer'


// Create styles
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#f7fafc'
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 40,
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 32,
    borderBottomWidth: 2,
    borderBottomColor: '#e2e8f0',
    paddingBottom: 12,
  },
  headerText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2d3748',
  },
  logo: {
    width: 50,
    height: 50,
    marginRight: 16,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 24,
    color: '#2d3748',
  },
  subtitle: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 32,
    color: '#4a5568',
  },
  section: {
    marginBottom: 24,
  },
  row: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  column: {
    flexDirection: 'column',
    flexGrow: 1,
  },
  label: {
    fontSize: 12,
    color: '#718096',
    marginBottom: 4,
    textTransform: 'uppercase',
  },
  value: {
    fontSize: 16,
    color: '#2d3748',
    fontWeight: 'bold',
  },
  photo: {
    width: 80,
    height: 80,
    borderRadius: 60,
    marginBottom: 24,
    alignSelf: 'center',
  },
  table: {
    display: 'table',
    width: 'auto',
    marginTop: 24,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 8,
  },
  tableRow: {
    flexDirection: 'row',
  },
  tableHeader: {
    backgroundColor: '#edf2f7',
  },
  tableCol: {
    width: '50%',
    borderRightWidth: 1,
    borderRightColor: '#e2e8f0',
  },
  tableCell: {
    padding: 12,
    fontSize: 12,
    textAlign: 'center',
  },
  footer: {
    marginTop: 20,
    textAlign: 'center',
    color: '#718096',
    fontSize: 10,
    fontStyle: 'italic',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
    paddingTop: 8,
  },
})

// Create Document Component
const VaccineCertificatePDF = ({ data, selectedVaccine }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      <View style={styles.card}>
        <View style={styles.header}>
          <Image
            style={styles.logo}
            src="/logo.png" // Replace with your actual logo
          />
          <Text style={styles.headerText}>Official Vaccination Certificate</Text>
        </View>

        <Text style={styles.title}>Certificate of {selectedVaccine.vaccine_name} Vaccination</Text>
        <Text style={styles.subtitle}>This is to certify that</Text>

        <Image
          style={styles.photo}
          src={data.user_info.user_photo || "/placeholder.png"}
        />

        <View style={styles.section}>
          <View style={styles.row}>
            <View style={styles.column}>
              <Text style={styles.label}>Name</Text>
              <Text style={styles.value}>{data.user_info.user_name}</Text>
            </View>
            <View style={styles.column}>
              <Text style={styles.label}>Email</Text>
              <Text style={styles.value}>{data.user_info.user_email}</Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Has completed the full course of vaccination for:</Text>
          <Text style={[styles.value, { fontSize: 12, marginTop: 8 }]}>
            {selectedVaccine.vaccine_name}
          </Text>
        </View>
        
        <View style={styles.table}>
          <View style={[styles.tableRow, styles.tableHeader]}>
            <View style={styles.tableCol}>
              <Text style={styles.tableCell}>Dose</Text>
            </View>
            <View style={styles.tableCol}>
              <Text style={styles.tableCell}>Date of Vaccination</Text>
            </View>
          </View>
          {selectedVaccine.doses.map((dose, index) => (
            <View style={styles.tableRow} key={index}>
              <View style={styles.tableCol}>
                <Text style={styles.tableCell}>{dose.dose_number}</Text>
              </View>
              <View style={styles.tableCol}>
                <Text style={styles.tableCell}>
                  {new Date(dose.vaccination_date).toLocaleDateString()}
                </Text>
              </View>
            </View>
          ))}
        </View>

        <Text style={styles.footer}>
          This certificate is issued based on the vaccination records in our system and is an official document certifying the completion of the {selectedVaccine.vaccine_name} vaccination series.
        </Text>
      </View>
    </Page>
  </Document>
)

export default VaccineCertificatePDF

