// Portuguese (pt) site-UI catalog. Mirrors the keys of ./en.ts exactly; only
// the values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const pt: Messages = {
  siteLanguageLabel: "Idioma do site",

  codeBlockCopied: "copiado ✓",
  codeBlockCopy: "copiar",

  headerTagline: "a revisão por pares é um bem público.",
  navSetup: "configurar",
  navSideBySide: "comparação",
  navGithub: "github ↗",

  bannerPausedDefault: "As submissões estão temporariamente em pausa.",
  bannerBusyPrefix: "O sistema está ocupado (",
  bannerBusySuffix: " lugares em uso). A sua revisão poderá ficar em fila de espera.",
  bannerFasterPrefix: "Para resultados mais rápidos, use a CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  heroGreetingPrefix: "Olá ",
  heroGreetingSuffix: " podes rever este artigo?",
  heroHeading: "‘coarse!",
  heroLede:
    "Agentes de IA revêem o seu artigo e escrevem um relatório de arbitragem. Você paga o custo da API diretamente. Sem conta.",
  heroManifesto:
    "A revisão por pares académica assenta em trabalho académico não remunerado. Outros decidiram fazer disso um negócio. Nós não gostámos disso.",

  scoreVsOthers: "vs. outros revisores de IA",
  statCostNum: "< $2*",
  statCostLabel: "por revisão",
  statCostFootnote: "*normalmente :)",
  statCommentsNum: "20+",
  statCommentsLabel: "comentários detalhados",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "código aberto",

  comparePrefix: "Avaliado às cegas contra",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Pontua mais alto em cobertura, especificidade e profundidade -- por uma fração do custo.",
  compareLink: "Veja a comparação →",

  formSubmitHeading: "Submeter um artigo",
  fieldPaper: "Artigo",
  dropzoneAriaLabel: "Carregue o seu artigo — largue um ficheiro ou clique para procurar",
  dropzoneInputAriaLabel: "Escolha um ficheiro para carregar",
  dropzoneReplaceSuffix: " MB — clique ou largue para substituir",
  dropzonePromptPrefix: "Largue o seu ficheiro aqui, ou ",
  dropzoneBrowse: "procurar",
  dropzoneMaxSize: "Até 50 MB",

  fieldEmail: "E-mail ",
  fieldEmailQualifier: "(apenas para revisão web)",
  emailPlaceholderUnavailable: "— indisponível —",
  emailPlaceholder: "voce@universidade.pt",
  emailAriaLabel: "Endereço de e-mail",
  emailHelperDisabled:
    "A entrega de e-mail está temporariamente em baixo. Guarde a sua chave de revisão ao submeter e volte daqui a cerca de uma hora.",
  emailHelperPrefix:
    "Enviaremos um e-mail quando estiver pronto. Verifique a pasta de spam se não o encontrar.",

  fieldKey: "Chave OpenRouter",
  fieldKeyGetOne: "obtenha uma →",
  keyOrPaste: "— ou cole uma chave —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "Chave de API OpenRouter",
  keyHelper:
    "As chaves OAuth permanecem apenas neste separador e são apagadas quando o fecha. Nunca são guardadas nos nossos servidores.",

  fieldNotes: "Notas para o revisor",
  fieldNotesOptional: "(opcional)",
  notesPlaceholder:
    "p. ex. concentre-se na estratégia de identificação no §3 — a secção de dados ainda é um marcador de posição.",
  notesAriaLabel: "Notas opcionais para orientar o revisor",
  notesHelper: "Oriente aquilo em que o revisor se foca. Não substitui a grelha de avaliação.",

  costEstimating: "A estimar o custo...",
  costEstimatePrefix: "Custo de API estimado: $",
  costUnavailable: "Estimativa de custo indisponível para este modelo",

  turnstileFailedLine1Prefix:
    "A nossa verificação humana não pôde ser concluída. Algo está a bloquear ou a atrasar ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — normalmente um modo de privacidade estrito do navegador (como a prevenção de rastreamento do Safari ou o Firefox ETP estrito), um bloqueador de conteúdos/anúncios (Brave Shields, uBlock Origin em algumas listas), ou uma rede lenta ou filtrada.",
  turnstileFailedLine2Prefix: "Tente primeiro recarregar a página. Se persistir, permita ",
  turnstileFailedLine2Mid: " para ",
  turnstileFailedLine2Suffix:
    " (desative os bloqueadores de conteúdos ou suavize as definições de privacidade), ou use um navegador diferente. Num URL de pré-visualização, a implementação poderá também precisar desse nome de anfitrião na lista de permissões do widget Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "Ou execute o coarse localmente com a sua própria chave OpenRouter: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  submitButton: "Rever o meu artigo",
  submitButtonBusy: "A submeter...",
  submitOr: "ou",
  handoffButton: "Rever com a minha subscrição ▾",
  handoffButtonBusy: "A preparar...",

  handoffUploading: "A carregar o artigo...",
  handoffPreparing: "A preparar a transferência...",

  explainReviewLabel: "Rever o meu artigo:",
  explainReviewBody:
    " O OpenRouter trata de tudo de ponta a ponta. O ficheiro é eliminado após o processamento. A chave de revisão funciona durante 90 dias. Normalmente menos de $2.",
  explainSubscriptionLabel: "Rever com a minha subscrição:",
  explainSubscriptionPart1:
    "entregamos-lhe um comando de shell que executa todo o pipeline do coarse localmente usando ",
  explainSubscriptionYour: "a sua",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", ou",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "subscrição para o raciocínio do LLM.",
  explainSubscriptionPdf:
    "Paga apenas ~$0,10 pelo passo local de Mistral OCR (com a sua própria chave OpenRouter); os carregamentos que não são PDF (.tex, .md, .docx, …) saltam o OCR e não precisam de chave OpenRouter.",
  explainSubscriptionNonPdf:
    "O seu ficheiro não é um PDF, por isso salta totalmente o passo de Mistral OCR — toda a execução é coberta pela sua subscrição, sem necessidade de chave OpenRouter.",
  explainSubscriptionPart3: "A revisão aparece nesta página quando estiver concluída.",
  explainDisclaimer:
    "É executado localmente na sua máquina usando a sua própria conta de Claude Code, Codex ou Gemini CLI. O coarse.ink não recebe nem armazena o seu início de sessão do fornecedor, e aplicam-se os termos, limites de utilização e políticas de organização do seu fornecedor. O coarse.ink não está associado à Anthropic, OpenAI ou Google.",

  handoffReviewWithPrefix: "Rever com ",
  handoffModelLabel: "modelo",
  handoffEffortLabel: "esforço",
  handoffPastePromptPrefix: "Cole este prompt no seu terminal do ",
  handoffPastePromptSuffix: ":",
  handoffRunHint:
    "O agente irá atualizar a skill coarse-review, executar toda a revisão localmente e demorar 10–25 minutos. O seu início de sessão do fornecedor permanece na sua máquina.",
  handoffKeyNeededPrefix:
    "A sua chave OpenRouter tem de estar primeiro na sua máquina — exporte ",
  handoffKeyEnvVar: "OPENROUTER_API_KEY",
  handoffKeyNeededMid1: ", ou coloque-a em ",
  handoffKeyEnvFile: ".env",
  handoffKeyNeededMid2: " ou ",
  handoffKeyConfigFile: "~/.coarse/config.toml",
  handoffKeyNeededSuffix:
    ". Não a passamos pelo navegador porque o URL de transferência acaba por ficar no registo de conversa do seu agente. Se estiver em falta, o agente irá pedi-la.",
  handoffKeyNotNeeded:
    "Não é necessária chave OpenRouter para este artigo — não é um PDF, por isso a extração é executada localmente sem o passo de Mistral OCR.",
  handoffReviewUrlIntro: "Quando a revisão terminar, aparecerá em:",
  handoffInstallPrefix: "Ainda não tem o ",
  handoffInstallSuffix: " ? ",
  handoffInstallLink: "instale-o →",

  findReviewHeading: "Encontrar uma revisão",
  findReviewPlaceholder: "Cole a sua chave de revisão, o link completo da revisão ou o ID de revisão antigo...",
  findReviewAriaLabel: "Chave de revisão",
  findReviewButton: "Encontrar",

  footerPrivacy: "privacidade",
  footerTerms: "termos",
  footerContact: "contacto",

  noticeKeyMigrated:
    "A sua chave OpenRouter guardada foi movida para um armazenamento que vale apenas para este separador. Será apagada quando fechar este separador.",
  errorLoginNoPersist:
    "Sessão iniciada, mas não foi possível manter a chave neste separador. Terá de a colar novamente se esta página recarregar.",
  errorLoginFailed:
    "O início de sessão do OpenRouter falhou. Tente novamente ou cole uma chave manualmente.",
  errorAuthFailed:
    "Autenticação falhada. Em implementações de pré-visualização, isto normalmente significa que as credenciais de Basic Auth em cache do navegador não foram enviadas na submissão do formulário. Atualize o separador (Cmd/Ctrl+Shift+R), inicie sessão novamente na solicitação de palavra-passe e tente outra vez.",
  errorServiceUnavailable: "Serviço temporariamente indisponível — tente novamente daqui a um minuto.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "O nosso widget de verificação humana não conseguiu carregar — provavelmente uma extensão do navegador (Brave Shields, uBlock Origin, Firefox ETP estrito) está a bloquear challenges.cloudflare.com. Tente desativá-la para ",
  errorTurnstileBlockedSuffix: ", ou execute o coarse localmente: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "Ainda à espera que a verificação humana carregue — aguarde um segundo e tente novamente.",
  errorPrepareUpload: "Falha ao preparar o carregamento",
  errorUploadFailed: "Falha no carregamento do ficheiro — tente novamente",
  errorSubmissionFailed: "Submissão falhada",
  errorHandoffFailed: "Transferência falhada",
  launchCommandCopied: "Comando copiado para a área de transferência. Cole-o no seu terminal.",
  launchOpeningCodex:
    "A abrir a aplicação de desktop do Codex — o compositor deverá ser preenchido previamente. Carregue em enviar.",
  launchOpeningPrefix: "A abrir ",
  launchOpeningSuffix: " — cole o prompt a partir da sua área de transferência (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " aplicação de desktop não abriu. Se só tiver a versão CLI instalada, cole antes os comandos acima no seu terminal.",
  errorLoginCouldNotStartPrefix: "Não foi possível iniciar o início de sessão do OpenRouter: ",

  reviewLanguageLabel: "Idioma da revisão",
  reviewLanguageAuto: "Automático — corresponder ao idioma do artigo",
  reviewLanguageHelper:
    "Por defeito, o próprio idioma do artigo; as citações permanecem sempre no original.",
};
