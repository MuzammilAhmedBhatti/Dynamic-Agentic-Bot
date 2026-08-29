{{- define "dynamic-agentic.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- define "dynamic-agentic.labels" -}}
app.kubernetes.io/name: {{ include "dynamic-agentic.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}
{{- define "dynamic-agentic.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dynamic-agentic.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
