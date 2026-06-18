// Portuguese (pt) site-UI catalog. Mirrors the keys of ./en.ts exactly; only
// the values are translated. Brand/technical tokens (coarse, OpenRouter, Claude
// Code, Codex, Gemini CLI, commands, URLs, model IDs) and glyphs are kept
// verbatim. Leading/trailing spaces on …Prefix/…Mid/…Suffix fragments are
// significant and match en.ts.

import type { Messages } from "@/lib/i18n";

export const pt: Messages = {
  // site language switcher (consumed by SiteLanguageSwitcher.tsx)
  siteLanguageLabel: "Idioma do site",

  // copy-to-clipboard code block
  codeBlockCopied: "copiado ✓",
  codeBlockCopy: "copiar",

  // header
  headerTagline: "a revisão por pares é um bem público.",
  navSetup: "configurar",
  navSideBySide: "comparação",
  navGithub: "github ↗",

  // capacity banner
  bannerPausedDefault: "As submissões estão temporariamente em pausa.",
  bannerBusyPrefix: "O sistema está ocupado (",
  bannerBusySuffix: " vagas em uso). A sua revisão poderá ficar em fila de espera.",
  bannerFasterPrefix: "Para resultados mais rápidos, experimente a CLI:",
  bannerPipInstall: "pip install coarse-ink",
  bannerGithub: "GitHub",

  // hero
  heroGreetingPrefix: "Olá ",
  heroGreetingSuffix: " podes rever este artigo?",
  heroHeading: "‘coarse!",
  heroLede:
    "Agentes de IA revêem o seu artigo e escrevem um parecer de revisão. Paga o custo da API diretamente. Sem conta.",
  heroManifesto:
    "A revisão por pares académica assenta em trabalho académico não remunerado. Outros decidiram fazer disso um negócio. Nós não gostámos.",

  // hero — score preview
  scoreVsOthers: "vs. outros revisores de IA",
  statCostNum: "< $2*",
  statCostLabel: "por revisão",
  statCostFootnote: "*normalmente :)",
  statCommentsNum: "20+",
  statCommentsLabel: "comentários detalhados",
  statOpenSourceNum: "MIT",
  statOpenSourceLabel: "código aberto",

  // hero — competitive comparison
  comparePrefix: "Avaliado às cegas contra",
  compareRefine: "refine.ink",
  compareStanford: "Stanford Agentic Reviewer",
  compareReviewer3: "reviewer3.com",
  compareSuffix:
    "Pontua mais alto em cobertura, especificidade e profundidade -- por uma fração do custo.",
  compareLink: "Veja a comparação →",

  // submit form — section heading + paper field
  formSubmitHeading: "Submeter um artigo",
  fieldPaper: "Artigo",
  dropzoneAriaLabel: "Carregue o seu artigo — largue um ficheiro ou clique para procurar",
  dropzoneInputAriaLabel: "Escolha um ficheiro para carregar",
  dropzoneReplaceSuffix: " MB — clique ou largue para substituir",
  dropzonePromptPrefix: "Largue o seu ficheiro aqui, ou ",
  dropzoneBrowse: "procurar",
  dropzoneMaxSize: "Até 50 MB",

  // submit form — email field
  fieldEmail: "E-mail ",
  fieldEmailQualifier: "(apenas para revisão na web)",
  emailPlaceholderUnavailable: "— indisponível —",
  emailPlaceholder: "voce@universidade.pt",
  emailAriaLabel: "Endereço de e-mail",
  emailHelperDisabled:
    "A entrega de e-mail está temporariamente indisponível. Guarde a sua chave de revisão ao submeter e volte daqui a cerca de uma hora.",
  emailHelperPrefix:
    "Enviamos-lhe um e-mail quando estiver pronto. Verifique a pasta de spam se não o encontrar.",

  // submit form — OpenRouter key field
  fieldKey: "Chave OpenRouter",
  fieldKeyGetOne: "obter uma →",
  keyOrPaste: "— ou cole uma chave —",
  keyPlaceholder: "sk-or-v1-…",
  keyAriaLabel: "Chave de API OpenRouter",
  keyHelper:
    "As chaves OAuth permanecem apenas neste separador e são apagadas quando o fecha. Nunca são guardadas nos nossos servidores.",

  // submit form — author notes
  fieldNotes: "Notas para o revisor",
  fieldNotesOptional: "(opcional)",
  notesPlaceholder:
    "p. ex. concentre-se na estratégia de identificação no §3 — a secção de dados ainda é um marcador de posição.",
  notesAriaLabel: "Notas opcionais para orientar o revisor",
  notesHelper: "Oriente aquilo em que o revisor se foca. Não substitui a grelha de avaliação.",

  // submit form — cost estimate
  costEstimating: "A estimar o custo...",
  costEstimatePrefix: "Custo de API estimado: $",
  costUnavailable: "Estimativa de custo indisponível para este modelo",

  // submit form — Turnstile failure block
  turnstileFailedLine1Prefix:
    "A nossa verificação humana não pôde ser concluída. Algo está a bloquear ou a atrasar ",
  turnstileChallengesHost: "challenges.cloudflare.com",
  turnstileFailedLine1Suffix:
    " — normalmente um modo de privacidade estrito do navegador (como a prevenção de rastreamento do Safari ou o Firefox ETP estrito), um bloqueador de conteúdos/anúncios (Brave Shields, uBlock Origin em algumas listas), ou uma rede lenta ou filtrada.",
  turnstileFailedLine2Prefix: "Experimente primeiro recarregar a página. Se persistir, permita ",
  turnstileFailedLine2Mid: " para ",
  turnstileFailedLine2Suffix:
    " (desative os bloqueadores de conteúdos ou suavize as definições de privacidade), ou use um navegador diferente. Num URL de pré-visualização, a implementação poderá também precisar desse nome de anfitrião na lista de permissões do widget Cloudflare Turnstile.",
  turnstileFailedLine3Prefix: "Ou execute o coarse localmente com a sua própria chave OpenRouter: ",
  turnstileUvxCommand: "uvx coarse-ink review paper.pdf",
  turnstileFailedLine3Suffix: ".",

  // submit form — buttons + handoff picker
  submitButton: "Rever o meu artigo",
  submitButtonBusy: "A submeter...",
  submitOr: "ou",
  handoffButton: "Rever com a minha subscrição ▾",
  handoffButtonBusy: "A preparar...",

  // submit form — handoff progress messages
  handoffUploading: "A carregar o artigo...",
  handoffPreparing: "A preparar a entrega...",

  // submit form — explanatory paragraphs
  explainReviewLabel: "Rever o meu artigo:",
  explainReviewBody:
    " O OpenRouter trata de tudo de ponta a ponta. O ficheiro é eliminado após o processamento. A chave de revisão funciona durante 90 dias. Normalmente menos de $2.",
  explainSubscriptionLabel: "Rever com a minha subscrição:",
  explainSubscriptionPart1:
    "entregamos-lhe um comando de shell que executa todo o pipeline do coarse localmente usando a ",
  explainSubscriptionYour: "sua",
  explainSubscriptionClaudeCode: "Claude Code",
  explainSubscriptionCommaCodex: ",",
  explainSubscriptionCodex: "Codex",
  explainSubscriptionOr: ", ou",
  explainSubscriptionGeminiCli: "Gemini CLI",
  explainSubscriptionPart2: "para o raciocínio do LLM.",
  explainSubscriptionPdf:
    "Paga apenas ~$0,10 pelo passo local do Mistral OCR (com a sua própria chave OpenRouter); os carregamentos que não são PDF (.tex, .md, .docx, …) saltam o OCR e não precisam de chave OpenRouter.",
  explainSubscriptionNonPdf:
    "O seu ficheiro não é um PDF, por isso salta totalmente o passo do Mistral OCR — toda a execução é coberta pela sua subscrição, sem necessidade de chave OpenRouter.",
  explainSubscriptionPart3: "A revisão aparece nesta página quando estiver concluída.",
  explainDisclaimer:
    "É executado localmente na sua máquina usando a sua própria conta de Claude Code, Codex ou Gemini CLI. O coarse.ink não recebe nem armazena o seu início de sessão do fornecedor, e aplicam-se os termos, limites de utilização e políticas de organização do seu fornecedor. O coarse.ink não está associado à Anthropic, OpenAI ou Google.",

  // submit form — handoff result card
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
    ". Não a passamos pelo navegador porque o URL de entrega acaba por ficar no registo de conversa do seu agente. Se estiver em falta, o agente irá pedi-la.",
  handoffKeyNotNeeded:
    "Não é necessária chave OpenRouter para este artigo — não é um PDF, por isso a extração é executada localmente sem o passo do Mistral OCR.",
  handoffReviewUrlIntro: "Quando a revisão terminar, aparecerá em:",
  handoffInstallPrefix: "Ainda não tem o ",
  handoffInstallSuffix: " ? ",
  handoffInstallLink: "instale-o →",

  // retrieve
  findReviewHeading: "Encontrar uma revisão",
  findReviewPlaceholder:
    "Cole a sua chave de revisão, o link completo da revisão ou o ID de revisão antigo...",
  findReviewAriaLabel: "Chave de revisão",
  findReviewButton: "Encontrar",

  // footer
  footerPrivacy: "privacidade",
  footerTerms: "termos",
  footerContact: "contacto",

  // status / errors (set in handlers)
  noticeKeyMigrated:
    "A sua chave OpenRouter guardada foi movida para um armazenamento que vale apenas para este separador. Será apagada quando fechar este separador.",
  errorLoginNoPersist:
    "Sessão iniciada, mas não foi possível manter a chave neste separador. Terá de a colar novamente se esta página recarregar.",
  errorLoginFailed:
    "O início de sessão do OpenRouter falhou. Tente novamente ou cole uma chave manualmente.",
  errorAuthFailed:
    "Falha na autenticação. Em implementações de pré-visualização, isto normalmente significa que as credenciais de Basic Auth em cache do navegador não foram enviadas na submissão do formulário. Atualize o separador (Cmd/Ctrl+Shift+R), inicie sessão novamente na solicitação de palavra-passe e tente outra vez.",
  errorServiceUnavailable: "Serviço temporariamente indisponível — tente novamente daqui a um minuto.",
  errorHttpMid: " (HTTP ",
  errorTurnstileBlockedPrefix:
    "O nosso widget de verificação humana não conseguiu carregar — provavelmente uma extensão do navegador (Brave Shields, uBlock Origin, Firefox ETP estrito) está a bloquear challenges.cloudflare.com. Tente desativá-la para ",
  errorTurnstileBlockedSuffix: ", ou execute o coarse localmente: uvx coarse-ink review paper.pdf",
  errorTurnstileWaiting:
    "Ainda à espera que a verificação humana carregue — aguarde um segundo e tente novamente.",
  errorPrepareUpload: "Falha ao preparar o carregamento",
  errorUploadFailed: "Falha no carregamento do ficheiro — tente novamente",
  errorSubmissionFailed: "Falha na submissão",
  errorHandoffFailed: "Falha na entrega",
  launchCommandCopied: "Comando copiado para a área de transferência. Cole-o no seu terminal.",
  launchOpeningCodex:
    "A abrir a aplicação de desktop do Codex — o compositor deverá ser preenchido previamente. Carregue em enviar.",
  launchOpeningPrefix: "A abrir ",
  launchOpeningSuffix: " — cole o prompt a partir da sua área de transferência (⌘V / Ctrl+V).",
  launchDidntOpenSuffix:
    " a aplicação de desktop não abriu. Se só tiver a versão CLI instalada, cole antes os comandos acima no seu terminal.",
  errorLoginCouldNotStartPrefix: "Não foi possível iniciar o início de sessão do OpenRouter: ",

  // review-language picker (LanguagePicker.tsx)
  reviewLanguageLabel: "Idioma da revisão",
  reviewLanguageAuto: "Automático — corresponder ao idioma do artigo",
  reviewLanguageHelper:
    "Por defeito, usa o próprio idioma do artigo; as citações permanecem sempre no original.",

  // model picker (ModelPicker.tsx)
  modelPickerLabel: "Modelo",
  modelPickerUnavailableTitle: "Atualmente indisponível",
  modelPickerSearchPlaceholder: "Procurar modelos...",
  modelPickerLoading: "A carregar modelos...",
  modelPickerNoResults: "Nenhum modelo encontrado.",
  modelPickerSearch: "procurar modelos...",

  // OpenRouter login button (OpenRouterLoginButton.tsx)
  openRouterConnected: "Ligado ao OpenRouter",
  openRouterLogOut: "Terminar sessão",
  openRouterLogIn: "Iniciar sessão com o OpenRouter →",

  // status page (status/[id]/page.tsx)
  statusAccessErrorNeedsKey:
    "Esta revisão requer o link seguro completo ou a chave de revisão.",
  statusLoadFailed: "Falha ao carregar o estado da revisão. Tente novamente.",
  statusCancelledByUser: "Revisão cancelada pelo utilizador",
  statusLoading: "A carregar",
  statusAccessTokenRequired: "Token de acesso necessário.",
  statusNotFoundHeading: "Revisão não encontrada.",
  statusNotFoundBody: "Verifique a chave de revisão e tente novamente.",
  statusCancelConfirmHeading: "Cancelar revisão?",
  statusCancelConfirmBody: "Tem a certeza? Não poderá ver os seus resultados.",
  statusCancelling: "A cancelar...",
  statusYesCancel: "Sim, cancelar",
  statusGoBack: "Voltar",
  statusLabelCancelled: "cancelada",
  statusLabelFailed: "falhou",
  statusLabelReviewing: "a rever",
  statusLabelQueued: "em fila",
  statusGithub: "GitHub ↗",
  statusReadingHeading: "A ler o seu artigo.",
  statusQueuedHeading: "Em fila.",
  statusRunningBody: "A executar o pipeline de revisão (normalmente 30–60 minutos).",
  statusQueuedBody: "A sua revisão está em fila e começará em breve.",
  statusEmailWhenDone: "Enviamos-lhe um e-mail quando estiver concluída.",
  statusCancelledHeading: "Revisão cancelada.",
  statusCancelledBody:
    "O trabalho em fila foi marcado como cancelado. Se o processamento já tinha começado, o worker poderá demorar algum tempo a parar.",
  statusFailedHeading: "Falhou.",
  statusUnexpectedError: "Ocorreu um erro inesperado.",
  statusResubmitPrefix: "Tente submeter novamente, ou publique o seu problema no ",
  statusResubmitGithub: "Github",
  statusResubmitSuffix: ".",
  statusTryAgain: "Tentar novamente →",
  statusKeyBoxSave: "A sua chave de revisão — guarde-a",
  statusKeyBoxLegacy: "Link de revisão antigo",
  statusCopied: "Copiado",
  statusCopyLink: "Copiar link",
  statusRedirectNote: "Esta página será redirecionada automaticamente quando a sua revisão estiver pronta.",
  statusCancelReview: "Cancelar revisão",

  // review page chrome (ReviewPageClient.tsx)
  reviewClientAccessErrorNeedsKey:
    "Esta revisão requer o link seguro completo ou a chave de revisão.",
  reviewClientLoadFailed: "Falha ao carregar a revisão. Tente novamente.",
  reviewClientLoading: "A carregar",
  reviewClientNotFoundHeading: "Revisão não encontrada.",
  reviewClientNotFoundBody: "Verifique a sua chave e tente novamente.",
  reviewClientSubmitNewPaper: "Submeter um novo artigo →",
  reviewClientAccessTokenRequired: "Token de acesso necessário.",
  reviewClientBackHome: "Voltar ao início →",
  reviewClientReadingHeading: "A ler o seu artigo.",
  reviewClientQueuedHeading: "Em fila.",
  reviewClientRunningBody: "Normalmente 30–60 minutos. Esta página atualiza-se automaticamente.",
  reviewClientQueuedBody: "O processamento começa em breve.",
  reviewClientFailedHeading: "A revisão falhou.",
  reviewClientUnexpectedError: "Ocorreu um erro inesperado.",
  reviewClientTryAgain: "Tentar novamente →",
  reviewClientCancelledHeading: "Revisão cancelada.",
  reviewClientCancelledBody: "Esta revisão foi cancelada antes de ser concluída.",

  // review page chrome (ReviewDisplay.tsx)
  reviewShowLess: "Mostrar menos",
  reviewShowMore: "Mostrar mais",
  reviewShowInPaper: "Mostrar no artigo",
  reviewMarkActive: "Marcar como ativo",
  reviewMarkDone: "Marcar como concluído",
  reviewDismiss: "Descartar",
  reviewDiscuss: "Discutir",
  reviewDiscussTitle: "Discutir este comentário com um modelo de IA",
  reviewShowDetails: "Mostrar detalhes",
  reviewStatusDone: "Concluído",
  reviewStatusDismissed: "Descartado",
  reviewHide: "Ocultar",
  reviewFilterAll: "Todos",
  reviewFilterActive: "Ativos",
  reviewFilterDone: "Concluídos",
  reviewFilterDismissed: "Descartados",
  reviewSidebarOverallFeedback: "Comentários Gerais",
  reviewSidebarCommentsPrefix: "Comentários (",
  reviewSidebarCommentsRemainingSuffix: " restantes)",
  reviewRemainingSuffix: " restantes",
  reviewDownload: "Transferir",
  reviewDownloadMarkdown: "Markdown (.md)",
  reviewDownloadPrint: "Imprimir / PDF",
  reviewHidePaper: "Ocultar Artigo",
  reviewShowPaper: "Mostrar Artigo",
  reviewCopied: "Copiado",
  reviewShare: "Partilhar",
  reviewGithub: "GitHub",
  reviewResizeAriaLabel: "Arraste para redimensionar o painel do artigo",
  reviewResizeTitle: "Arraste para redimensionar",
  reviewOfPrefix: "Revisão de ",
  reviewMetaModel: "Modelo",
  reviewMetaDate: "Data",
  reviewMetaDomain: "Domínio",
  reviewMetaTime: "Tempo",
  reviewMetaCost: "Custo",
  reviewMetaReviewLanguage: "Idioma da revisão",
  reviewMetaAutoDetectedSuffix: " · detetado automaticamente",
  reviewOverallFeedbackHeading: "Comentários Gerais",
  reviewDetailedCommentsPrefix: "Comentários Detalhados (",
  reviewDetailedCommentsSuffix: ")",
  reviewGeneratedByPrefix: "Gerado por ",
  reviewGeneratedBySuffix: ". Claro.",
  reviewShareThisReview: "Partilhar esta revisão",
  reviewDeleteReview: "Eliminar revisão",
  reviewDeleteConfirmHeading: "Eliminar revisão?",
  reviewDeleteConfirmBody: "Tem a certeza? Não poderá ver os seus resultados.",
  reviewDeleting: "A eliminar...",
  reviewYesDelete: "Sim, eliminar",
  reviewGoBack: "Voltar",

  // review page chrome — comment chat (CommentChat.tsx)
  chatExamplePrompt1: "Esta crítica está realmente correta?",
  chatExamplePrompt2: "Como devo rever o texto para a resolver?",
  chatExamplePrompt3: "Em que parte do artigo é que isto se aplica?",
  chatNoResponse: "Sem resposta do modelo. Tente novamente ou mude de modelo.",
  chatSessionExpired: "A sua sessão do OpenRouter expirou. Inicie sessão novamente para continuar.",
  chatSomethingWrong: "Algo correu mal.",
  chatDiscussKicker: "Discutir · ",
  chatKickerComment: "comentário #",
  chatKickerOverallFeedback: "comentários gerais",
  chatDiscussAriaPrefix: "Discutir: ",
  chatCloseAriaLabel: "Fechar conversa",
  chatDisconnectKeyTitle:
    "Desligar a sua chave OpenRouter (não é guardada para além deste separador)",
  chatDisconnectKey: "Desligar chave",
  chatInputPlaceholder: "Pergunte sobre este comentário…",
  chatMessageAriaLabel: "Mensagem",
  chatStop: "Parar",
  chatSend: "Enviar",
  chatModelDisclosurePrefix: "Modelo: ",
  chatKeyGateIntro:
    "Ligue o OpenRouter para conversar sobre este comentário. A sua chave é enviada diretamente para o OpenRouter — nunca para os nossos servidores — e é apagada quando fecha este separador.",
  chatKeyGateOrPaste: "— ou cole uma chave —",
  chatKeyGatePlaceholder: "sk-or-v1-…",
  chatKeyGateAriaLabel: "Chave de API OpenRouter",
  chatKeyGateUseKey: "Usar chave",
  chatKeyGateHelper:
    "As chaves OAuth permanecem apenas neste separador e são apagadas quando o fecha. Nunca são guardadas nos nossos servidores.",
  chatEmptyHintPrefix: "Pergunte o que quiser sobre este comentário. Cada mensagem envia ",
  chatEmptyHintFullPaper: "o artigo completo",
  chatEmptyHintQuotedPassage: "a passagem citada e o feedback",
  chatEmptyHintSuffix: " como contexto e usa os seus créditos do OpenRouter.",
  chatEmptyHintNoPaper:
    "O texto completo do artigo não é guardado para esta revisão, por isso as respostas baseiam-se apenas na passagem citada e no feedback.",

  // review page chrome — subscription handoff menu (SubscriptionHandoffMenu.tsx)
  handoffMenuOpenedPromptPrefix: "Abriu ",
  handoffMenuOpenedPromptMid: " com o prompt preenchido — anexe coarse_",
  handoffMenuOpenedPromptSuffix:
    "_context.md e depois envie. (O prompt também foi copiado, por precaução.)",
  handoffMenuOpenedPlainMid: " — anexe coarse_",
  handoffMenuOpenedPlainSuffix: "_context.md e cole o prompt copiado.",
  handoffMenuButtonTitle:
    "Envie o artigo + revisão para a sua própria conversa de IA (Claude, ChatGPT, Gemini, Grok, DeepSeek)",
  handoffMenuButton: "Discutir com a sua IA",
  handoffMenuDownloadsIntro: "Transfere o artigo + revisão e depois abre:",

  // review page chrome — paper panel (PaperPanel.tsx)
  paperPanelHeading: "Artigo",
  paperPanelDownload: "Transferir",
  paperPanelDownloadAriaLabel: "Transferir o markdown do artigo",
  paperPanelCloseAriaLabel: "Fechar painel do artigo",
};
