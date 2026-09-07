import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Box, Button, Paper, Typography } from "@mui/material";

import { apiFetch, ApiError } from "../api/client";
import { LoadingState, ErrorState } from "../components/AsyncState";
import type { ArticleDetail } from "../types/domain";

export default function ArticleDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["article", slug],
    queryFn: () => apiFetch<ArticleDetail>(`/api/v1/articles/${slug}`),
    enabled: Boolean(slug),
  });

  const feedbackMutation = useMutation({
    mutationFn: (resolved: boolean) =>
      apiFetch(`/api/v1/articles/${query.data!.id}/feedback`, {
        method: "PUT",
        body: JSON.stringify({ resolved }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["article", slug] }),
  });

  if (query.isLoading) return <LoadingState label="Carregando artigo..." />;
  if (query.isError) {
    const message = query.error instanceof ApiError ? query.error.message : "Erro ao carregar o artigo.";
    return <ErrorState message={message} onRetry={() => query.refetch()} />;
  }

  const article = query.data!;

  function handleNotResolved() {
    feedbackMutation.mutate(false);
    navigate("/chamados/novo", { state: { title: article.title, category: article.category } });
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        {article.title}
      </Typography>
      <Typography sx={{ whiteSpace: "pre-line", mb: 3 }}>{article.content}</Typography>

      <Typography variant="subtitle1" gutterBottom>
        Este artigo resolveu sua duvida?
      </Typography>
      <Box sx={{ display: "flex", gap: 2 }}>
        <Button variant="contained" color="success" onClick={() => feedbackMutation.mutate(true)}>
          Sim, resolveu
        </Button>
        <Button variant="outlined" color="warning" onClick={handleNotResolved}>
          Nao resolveu, abrir chamado
        </Button>
      </Box>
    </Paper>
  );
}