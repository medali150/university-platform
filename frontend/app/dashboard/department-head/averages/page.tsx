"use client";

import React, { useState, useEffect } from "react";
import { useRequireRole } from "@/hooks/useRequireRole";
import { Role } from "@/types/auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Users,
  TrendingUp,
  Award,
  AlertTriangle,
  Eye,
  FileText,
  Send,
  RefreshCw,
  CheckCircle2,
  Search,
  Download,
  Filter,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

interface StudentSummary {
  student_id: string;
  student_name: string;
  student_email: string;
  groupe: string;
  niveau: string;
  specialite: string;
  moyenne_generale: number | null;
  rang: number | null;
  total_matieres: number;
  matieres_validees: number;
  status: string;
}

interface Statistics {
  total_students: number;
  students_with_grades: number;
  average_generale: number;
  highest_average: number;
  lowest_average: number;
  excellent_count: number;
  good_count: number;
  average_count: number;
  needs_improvement_count: number;
}

interface SubjectDetail {
  matiere_id: string;
  matiere_nom: string;
  coefficient: number;
  moyenne: number;
  validee: boolean;
  observation: string | null;
  grades: Grade[];
}

interface Grade {
  id: string;
  valeur: number;
  type: string;
  coefficient: number;
  date_examen: string | null;
  enseignant: string;
  observation: string | null;
}

interface StudentDetail {
  student: {
    id: string;
    nom: string;
    prenom: string;
    email: string;
    groupe: string;
    niveau: string;
    specialite: string;
  };
  moyenne_generale: number | null;
  rang: number | null;
  validee: boolean;
  observation: string | null;
  subjects: SubjectDetail[];
  semestre: string;
  annee_scolaire: string;
}

export default function StudentAveragesPage() {
  const { user, isLoading: authLoading } = useRequireRole("DEPARTMENT_HEAD" as Role);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<StudentDetail | null>(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [showValidateDialog, setShowValidateDialog] = useState(false);
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [selectedStudentIds, setSelectedStudentIds] = useState<string[]>([]);
  const [validationObservation, setValidationObservation] = useState("");
  const [sendNotification, setSendNotification] = useState(true);
  const [sendEmail, setSendEmail] = useState(true);

  // Filters
  const [semestre, setSemestre] = useState("SEMESTER_1");
  const [anneeScolaire, setAnneeScolaire] = useState("2024-2025");
  const [groupeFilter, setGroupeFilter] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (user && !authLoading) {
      fetchDashboardData();
    }
  }, [user, authLoading, semestre, anneeScolaire, groupeFilter]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const data = await api.getAveragesDashboard({
        semestre,
        annee_scolaire: anneeScolaire,
        ...(groupeFilter && { groupe_id: groupeFilter }),
      });

      console.log("Dashboard data received:", data);
      setStatistics(data.statistics);
      setStudents(data.students);
    } catch (error: any) {
      console.error("Error fetching dashboard:", error);
      const errorMessage = error?.message || error?.detail || "Impossible de charger les données";
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const calculateAverages = async () => {
    try {
      setCalculating(true);

      const result = await api.calculateAverages({
        semestre,
        annee_scolaire: anneeScolaire,
        ...(groupeFilter && { groupe_id: groupeFilter }),
      });
      
      toast.success(`Moyennes calculées pour ${result.calculated_count} étudiants`);

      fetchDashboardData();
    } catch (error) {
      console.error("Error calculating averages:", error);
      toast.error("Impossible de calculer les moyennes");
    } finally {
      setCalculating(false);
    }
  };

  const viewStudentDetail = async (studentId: string) => {
    try {
      const data = await api.getStudentAveragesDetail(studentId, {
        semestre,
        annee_scolaire: anneeScolaire,
      });

      setSelectedStudent(data);
      setShowDetailDialog(true);
    } catch (error) {
      console.error("Error fetching student detail:", error);
      toast.error("Impossible de charger les détails");
    }
  };

  const validateAverages = async () => {
    try {
      const result = await api.validateAverages({
        student_ids: selectedStudentIds,
        semestre,
        annee_scolaire: anneeScolaire,
        observation: validationObservation || undefined,
      });
      
      toast.success(`Moyennes validées pour ${result.validated_count} étudiants`);

      setShowValidateDialog(false);
      setSelectedStudentIds([]);
      setValidationObservation("");
      fetchDashboardData();
    } catch (error) {
      console.error("Error validating averages:", error);
      toast.error("Impossible de valider les moyennes");
    }
  };

  const generateReports = async () => {
    try {
      const result = await api.generateGradeReports({
        student_ids: selectedStudentIds,
        semestre,
        annee_scolaire: anneeScolaire,
        send_notification: sendNotification,
        send_email: sendEmail,
      });
      
      toast.success(`${result.generated_count} relevés générés`);

      setShowReportDialog(false);
      setSelectedStudentIds([]);
    } catch (error) {
      console.error("Error generating reports:", error);
      toast.error("Impossible de générer les relevés");
    }
  };

  const getStatusBadge = (status: string) => {
    const configs = {
      excellent: { label: "Excellent", className: "bg-green-500" },
      good: { label: "Bien", className: "bg-blue-500" },
      average: { label: "Passable", className: "bg-yellow-500" },
      needs_improvement: { label: "Insuffisant", className: "bg-red-500" },
      no_grades: { label: "Pas de notes", className: "bg-gray-500" },
    };

    const config = configs[status as keyof typeof configs] || configs.no_grades;
    return (
      <Badge className={config.className}>
        {config.label}
      </Badge>
    );
  };

  const getGradeTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      EXAM: "Examen",
      CONTINUOUS: "Contrôle Continu",
      PRACTICAL: "TP",
      PROJECT: "Projet",
      ORAL: "Oral",
    };
    return labels[type] || type;
  };

  const filteredStudents = students.filter((student) =>
    student.student_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.student_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.groupe.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <RefreshCw className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gestion des Moyennes</h1>
          <p className="text-muted-foreground">
            Consultation et validation des moyennes des étudiants
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={calculateAverages} disabled={calculating}>
            <RefreshCw className={`h-4 w-4 mr-2 ${calculating ? "animate-spin" : ""}`} />
            Calculer les Moyennes
          </Button>
          {selectedStudentIds.length > 0 && (
            <>
              <Button
                variant="outline"
                onClick={() => setShowValidateDialog(true)}
              >
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Valider ({selectedStudentIds.length})
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowReportDialog(true)}
              >
                <FileText className="h-4 w-4 mr-2" />
                Générer Relevés ({selectedStudentIds.length})
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Étudiants
              </CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_students}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.students_with_grades} avec notes
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Moyenne Générale
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics.average_generale.toFixed(2)}/20
              </div>
              <p className="text-xs text-muted-foreground">
                Min: {statistics.lowest_average.toFixed(2)} | Max: {statistics.highest_average.toFixed(2)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Excellents
              </CardTitle>
              <Award className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {statistics.excellent_count}
              </div>
              <p className="text-xs text-muted-foreground">
                Bien: {statistics.good_count}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                À Améliorer
              </CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {statistics.needs_improvement_count}
              </div>
              <p className="text-xs text-muted-foreground">
                Passable: {statistics.average_count}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filtres</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-2">
              <Label>Semestre</Label>
              <Select value={semestre} onValueChange={setSemestre}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="SEMESTER_1">Semestre 1</SelectItem>
                  <SelectItem value="SEMESTER_2">Semestre 2</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Année Scolaire</Label>
              <Select value={anneeScolaire} onValueChange={setAnneeScolaire}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="2024-2025">2024-2025</SelectItem>
                  <SelectItem value="2023-2024">2023-2024</SelectItem>
                  <SelectItem value="2022-2023">2022-2023</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Rechercher</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Nom, email, groupe..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            <div className="flex items-end">
              <Button variant="outline" onClick={fetchDashboardData}>
                <Filter className="h-4 w-4 mr-2" />
                Actualiser
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Students Table */}
      <Card>
        <CardHeader>
          <CardTitle>Liste des Étudiants</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox
                    checked={
                      selectedStudentIds.length === filteredStudents.length &&
                      filteredStudents.length > 0
                    }
                    onCheckedChange={(checked) => {
                      if (checked) {
                        setSelectedStudentIds(
                          filteredStudents.map((s) => s.student_id)
                        );
                      } else {
                        setSelectedStudentIds([]);
                      }
                    }}
                  />
                </TableHead>
                <TableHead>Étudiant</TableHead>
                <TableHead>Groupe</TableHead>
                <TableHead>Niveau</TableHead>
                <TableHead>Moyenne</TableHead>
                <TableHead>Rang</TableHead>
                <TableHead>Matières</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredStudents.map((student) => (
                <TableRow key={student.student_id}>
                  <TableCell>
                    <Checkbox
                      checked={selectedStudentIds.includes(student.student_id)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setSelectedStudentIds([...selectedStudentIds, student.student_id]);
                        } else {
                          setSelectedStudentIds(
                            selectedStudentIds.filter((id) => id !== student.student_id)
                          );
                        }
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <div>
                      <div className="font-medium">{student.student_name}</div>
                      <div className="text-xs text-muted-foreground">
                        {student.student_email}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{student.groupe}</TableCell>
                  <TableCell>{student.niveau}</TableCell>
                  <TableCell>
                    <span className="font-bold text-lg">
                      {student.moyenne_generale !== null
                        ? `${student.moyenne_generale.toFixed(2)}/20`
                        : "—"}
                    </span>
                  </TableCell>
                  <TableCell>
                    {student.rang !== null ? (
                      <Badge variant="outline">#{student.rang}</Badge>
                    ) : (
                      "—"
                    )}
                  </TableCell>
                  <TableCell>
                    <span className="text-sm">
                      {student.matieres_validees}/{student.total_matieres}
                    </span>
                  </TableCell>
                  <TableCell>{getStatusBadge(student.status)}</TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => viewStudentDetail(student.student_id)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Student Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Détails des Notes</DialogTitle>
            <DialogDescription>
              {selectedStudent && (
                <div className="mt-2">
                  <div className="font-semibold text-lg">
                    {selectedStudent.student.prenom} {selectedStudent.student.nom}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {selectedStudent.student.groupe} | {selectedStudent.student.niveau}
                  </div>
                  {selectedStudent.moyenne_generale && (
                    <div className="mt-2 flex items-center gap-4">
                      <span className="text-xl font-bold">
                        Moyenne: {selectedStudent.moyenne_generale.toFixed(2)}/20
                      </span>
                      {selectedStudent.rang && (
                        <Badge variant="outline">Rang: #{selectedStudent.rang}</Badge>
                      )}
                      {selectedStudent.validee && (
                        <Badge className="bg-green-500">✓ Validée</Badge>
                      )}
                    </div>
                  )}
                </div>
              )}
            </DialogDescription>
          </DialogHeader>

          {selectedStudent && (
            <div className="space-y-4">
              {selectedStudent.subjects.map((subject) => (
                <Card key={subject.matiere_id}>
                  <CardHeader>
                    <div className="flex justify-between items-center">
                      <CardTitle className="text-lg">{subject.matiere_nom}</CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">Coef: {subject.coefficient}</Badge>
                        <Badge className={subject.moyenne >= 10 ? "bg-green-500" : "bg-red-500"}>
                          {subject.moyenne.toFixed(2)}/20
                        </Badge>
                        {subject.validee && (
                          <Badge className="bg-green-500">✓</Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Type</TableHead>
                          <TableHead>Note</TableHead>
                          <TableHead>Coef</TableHead>
                          <TableHead>Date</TableHead>
                          <TableHead>Enseignant</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {subject.grades.map((grade) => (
                          <TableRow key={grade.id}>
                            <TableCell>{getGradeTypeLabel(grade.type)}</TableCell>
                            <TableCell className="font-bold">
                              {grade.valeur.toFixed(2)}/20
                            </TableCell>
                            <TableCell>{grade.coefficient}</TableCell>
                            <TableCell>
                              {grade.date_examen
                                ? new Date(grade.date_examen).toLocaleDateString("fr-FR")
                                : "—"}
                            </TableCell>
                            <TableCell className="text-sm">{grade.enseignant}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Validate Dialog */}
      <Dialog open={showValidateDialog} onOpenChange={setShowValidateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Valider les Moyennes</DialogTitle>
            <DialogDescription>
              Vous allez valider les moyennes de {selectedStudentIds.length} étudiant(s)
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Observation (optionnelle)</Label>
              <Textarea
                placeholder="Ajouter un commentaire..."
                value={validationObservation}
                onChange={(e) => setValidationObservation(e.target.value)}
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowValidateDialog(false)}>
              Annuler
            </Button>
            <Button onClick={validateAverages}>
              <CheckCircle2 className="h-4 w-4 mr-2" />
              Valider
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Generate Reports Dialog */}
      <Dialog open={showReportDialog} onOpenChange={setShowReportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Générer les Relevés de Notes</DialogTitle>
            <DialogDescription>
              Générer les relevés pour {selectedStudentIds.length} étudiant(s)
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="notification"
                checked={sendNotification}
                onCheckedChange={(checked) => setSendNotification(checked as boolean)}
              />
              <Label htmlFor="notification">Envoyer une notification</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="email"
                checked={sendEmail}
                onCheckedChange={(checked) => setSendEmail(checked as boolean)}
              />
              <Label htmlFor="email">Envoyer par email</Label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReportDialog(false)}>
              Annuler
            </Button>
            <Button onClick={generateReports}>
              <FileText className="h-4 w-4 mr-2" />
              Générer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
