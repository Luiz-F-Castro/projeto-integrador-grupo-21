import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Alert, Button, MenuItem, Paper, TextField, Typography } from "@mui/material";

import { apiFetch, ApiError } from "../api/client";
import type { TicketCategory, TicketDetail } from "../types/domain";

const CATEGORIES: { value: TicketCategory; label: string }[] = [
  { value: "ACCESS", label: "Acesso" },
  { value: "SOFTWARE", label: "Software" },
  { value: "NETWORK", label: "Rede" },
  { value: "HARDWARE", label: "Hardware" },
  { value: "SECURITY", label: "Seguranca" },
  { value: "OTHER", label: "Outro" },
];

export default function NewTicketPage() {
  const navigate = useNavigate();
  const location = useLocation() as { state?: { title?: string; category?: TicketCategory } };

  const [title, setTitle] = useState(location.state?.title ?? "");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<TicketCategory>(location.state?.category ?? "OTHER");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      apiFetch<TicketDetail>("/api/v1/tickets", {
        method: "POST",
        body: JSON.stringify({ title, description, category }),
      }),
    onSuccess: (ticket) => navigate(`/chamados/${ticket.id}`),
    onError: (err) => setErrorMessage(err instanceof ApiError ? err.message : "Erro ao abrir chamado."),
  });

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    mutation.mutate();
  }

  return (
    <Paper sx={{ p: 3, maxWidth: 560 }} component="form" onSubmit={handleSubmit}>
      <Typography variant="h5" gutterBottom>
        Abrir novo chamado
      </Typography>

      {errorMessage && <Alert severity="error" sx={{ mb: 2 }}>{errorMessage}</Alert>}

      <TextField
        label="Titulo"
        fullWidth
        margin="normal"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        helperText="Entre 5 e 160 caracteres"
        required
      />
      <TextField
        select
        label="Categoria"
        fullWidth
        margin="normal"
        value={category}
        onChange={(event) => setCategory(event.target.value as TicketCategory)}
      >
        {CATEGORIES.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            {option.label}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        label="Descricao"
        fullWidth
        margin="normal"
        multiline
        minRows={4}
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        helperText="Entre 10 e 2000 caracteres"
        required
      />

      <Button type="submit" variant="contained" sx={{ mt: 2 }} disabled={mutation.isPending}>
        {mutation.isPending ? "Enviando..." : "Abrir chamado"}
      </Button>
    </Paper>
  );
}