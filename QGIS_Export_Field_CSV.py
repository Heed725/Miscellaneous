"""
QGIS Processing Script: Export Shapefile Fields to CSV
This script exports selected fields from a shapefile to a CSV file with fields as columns.
"""

from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterBoolean)
from qgis import processing
import csv


class ExportFieldsToCsv(QgsProcessingAlgorithm):
    """
    Export selected fields from a shapefile to CSV with fields as columns.
    """
    
    INPUT = 'INPUT'
    FIELDS = 'FIELDS'
    UNIQUE_ONLY = 'UNIQUE_ONLY'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        """
        Define the inputs and output of the algorithm.
        """
        # Input vector layer (shapefile)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                'Input shapefile',
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        # Field selection (multiple fields allowed)
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELDS,
                'Select fields to export',
                None,
                self.INPUT,
                QgsProcessingParameterField.Any,
                allowMultiple=True
            )
        )
        
        # Checkbox for unique values only
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.UNIQUE_ONLY,
                'Export unique values only (remove duplicates)',
                defaultValue=True
            )
        )
        
        # Output CSV file
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                'Output CSV file',
                'CSV files (*.csv)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Process the algorithm.
        """
        # Get parameters
        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        fields = self.parameterAsFields(parameters, self.FIELDS, context)
        unique_only = self.parameterAsBoolean(parameters, self.UNIQUE_ONLY, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        
        if not layer:
            feedback.reportError('Invalid input layer')
            return {}
        
        if not fields:
            feedback.reportError('No fields selected')
            return {}
        
        feedback.pushInfo(f'Exporting {len(fields)} fields from {layer.name()}')
        feedback.pushInfo(f'Fields: {", ".join(fields)}')
        feedback.pushInfo(f'Mode: {"Unique values only" if unique_only else "All values (including duplicates)"}')
        
        # Get total number of features for progress reporting
        total = layer.featureCount()
        
        if unique_only:
            # Collect unique combinations of field values
            unique_rows = set()
            
            feedback.pushInfo('Collecting unique field combinations...')
            
            for current, feature in enumerate(layer.getFeatures()):
                if feedback.isCanceled():
                    break
                
                # Extract values for selected fields
                row_values = []
                for field in fields:
                    value = feature[field]
                    # Handle NULL values
                    if value is None:
                        value = ''
                    row_values.append(str(value))
                
                # Add tuple to set (sets only store unique values)
                unique_rows.add(tuple(row_values))
                
                # Update progress
                feedback.setProgress(int(current / total * 50))
            
            feedback.pushInfo(f'Found {len(unique_rows)} unique combinations out of {total} features')
            
            # Write unique rows to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header row with field names
                writer.writerow(fields)
                
                # Write unique data rows (sorted for consistency)
                for current, row in enumerate(sorted(unique_rows)):
                    if feedback.isCanceled():
                        break
                    
                    writer.writerow(row)
                    
                    # Update progress
                    feedback.setProgress(50 + int(current / len(unique_rows) * 50))
            
            feedback.pushInfo(f'Successfully exported {len(unique_rows)} unique rows to {output_file}')
        
        else:
            # Export all values including duplicates
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header row with field names
                writer.writerow(fields)
                
                # Write all data rows
                for current, feature in enumerate(layer.getFeatures()):
                    if feedback.isCanceled():
                        break
                    
                    # Extract values for selected fields
                    row = []
                    for field in fields:
                        value = feature[field]
                        # Handle NULL values
                        if value is None:
                            value = ''
                        row.append(value)
                    
                    writer.writerow(row)
                    
                    # Update progress
                    feedback.setProgress(int(current / total * 100))
            
            feedback.pushInfo(f'Successfully exported {total} rows to {output_file}')
        
        return {self.OUTPUT: output_file}

    def name(self):
        """
        Returns the algorithm name.
        """
        return 'exportfieldstocsv'

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return 'Export Fields to CSV'

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return 'Export Tools'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to.
        """
        return 'exporttools'

    def createInstance(self):
        """
        Creates a new instance of the algorithm.
        """
        return ExportFieldsToCsv()

    def shortHelpString(self):
        """
        Returns a short help string for the algorithm.
        """
        return """
        This algorithm exports selected fields from a shapefile to a CSV file.
        
        Parameters:
        - Input shapefile: The vector layer to export from
        - Select fields: Choose one or more fields to export (hold Ctrl to select multiple)
        - Export unique values only: 
          * Checked (default): Only export unique combinations, remove duplicates
          * Unchecked: Export all values including duplicates
        - Output CSV: The destination CSV file path
        
        When "unique values only" is checked:
        - Only unique combinations of the selected field values are exported
        - Results are sorted alphabetically for consistency
        - Shows statistics about unique vs total features
        
        When "unique values only" is unchecked:
        - All features are exported, including duplicate combinations
        - One row per feature in the original order
        
        NULL values will be exported as empty strings.
        """
