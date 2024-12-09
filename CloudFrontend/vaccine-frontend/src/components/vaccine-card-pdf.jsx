import React from 'react'
import { Document, Page, Text, View, StyleSheet, Image, Font } from '@react-pdf/renderer'
// Register custom fonts

// Create styles
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#f8fafc',
    padding: 30,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 32,
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
    borderBottomWidth: 2,
    borderBottomColor: '#f1f5f9',
    paddingBottom: 20,
  },
  headerText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  logo: {
    width: 48,
    height: 48,
    marginRight: 16,
  },
  section: {
    marginBottom: 5,
  },
  row: {
    flexDirection: 'row',
    marginBottom: 12,
    flexWrap: 'wrap',
    gap: 16,
  },
  column: {
    flexDirection: 'column',
    minWidth: '45%',
    flexGrow: 1,
  },
  label: {
    fontSize: 8,
    color: '#64748b',
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  value: {
    fontSize: 12,
    color: '#1e293b',
    fontWeight: 'bold',
    lineHeight: 1.4,
  },
  photo: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 12,
    alignSelf: 'center',
  },
  table: {
    display: 'table',
    width: 'auto',
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#f1f5f9',
    borderRadius: 8,
    overflow: 'hidden',
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  tableHeader: {
    backgroundColor: '#f8fafc',
  },
  tableCol: {
    width: '33%',
    borderRightWidth: 1,
    borderRightColor: '#f1f5f9',
  },
  tableCell: {
    padding: 12,
    fontSize: 11,
    textAlign: 'center',
    color: '#475569',
  },
  footer: {
    marginTop: 32,
    textAlign: 'center',
    color: '#64748b',
    fontSize: 9,
    fontStyle: 'italic',
    lineHeight: 1.5,
  },
})

// Create Document Component
const VaccineCardPDF = ({ data, selectedVaccine }) => (
  <Document>
    <Page size={[400, 650]} style={styles.page}>
      <View style={styles.card}>
        <View style={styles.header}>
          <Image
            style={styles.logo}
            src="/logo.png" // Replace with your actual logo
          />
          <Text style={styles.headerText}>Vaccination Card</Text>
        </View>

        {/* <Image
          style={styles.photo}
          src={data.user_info.user_photo || "/placeholder.svg"}
        /> */}
        
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
          <Text style={styles.label}>Vaccine</Text>
          <Text style={styles.value}>{selectedVaccine.vaccine_name}</Text>
        </View>
        
        <View style={styles.table}>
          <View style={[styles.tableRow, styles.tableHeader]}>
            <View style={styles.tableCol}>
              <Text style={styles.tableCell}>Dose</Text>
            </View>
            <View style={styles.tableCol}>
              <Text style={styles.tableCell}>Date</Text>
            </View>
            <View style={styles.tableCol}>
              <Text style={styles.tableCell}>Status</Text>
            </View>
          </View>
          {selectedVaccine.doses.map((dose, index) => (
            <View style={styles.tableRow} key={index}>
              <View style={styles.tableCol}>
                <Text style={styles.tableCell}>{dose.dose_number}</Text>
              </View>
              <View style={styles.tableCol}>
                <Text style={styles.tableCell}>
                  {dose.vaccination_date ? new Date(dose.vaccination_date).toLocaleDateString() : 'N/A'}
                </Text>
              </View>
              <View style={styles.tableCol}>
                <Text style={styles.tableCell}>{dose.is_taken ? 'Taken' : 'Pending'}</Text>
              </View>
            </View>
          ))}
        </View>

        <Text style={styles.footer}>
          This vaccination card is an official record of your {selectedVaccine.vaccine_name} vaccination.
        </Text>
      </View>
    </Page>
  </Document>
)

export default VaccineCardPDF

