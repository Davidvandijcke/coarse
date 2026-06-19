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

  // setup page (setup/page.tsx)
  // setup page — tab switcher
  setupTablistAriaLabel: "Caminho de configuração",
  setupTabOpenRouter: "Chave OpenRouter",
  setupTabSubscription: "Usar a minha subscrição",
  // setup page — OpenRouter tab intro
  setupOrHeading: "Obtenha a sua chave OpenRouter",
  setupOrIntro:
    "Demora cerca de 2 minutos. Vai precisar de um cartão de crédito para ~$1 em créditos para começar — irá carregar até $20 no passo 2.",
  setupOrFasterLabel: "Opção mais rápida:",
  setupOrFasterMid1: " no formulário principal pode clicar em ",
  setupOrFasterLogIn: "“Iniciar sessão com o OpenRouter”",
  setupOrFasterSuffix:
    " para autorizar o coarse e saltar a criação manual da chave. Continua a precisar de uma conta OpenRouter com créditos (passos 1 e 2 abaixo), e continuamos a recomendar definir um limite de gastos por chave (passo 4).",
  // setup page — OpenRouter step 1
  setupOrStep1Title: "Criar uma conta",
  setupOrStep1BodyPrefix: "Vá a ",
  setupOrStep1BodySuffix: " e clique em “Get API Key” ou registe-se com Google / GitHub.",
  setupOrStep1Annotation: "página inicial",
  setupOrStep1MockButton: "Get API Key",
  setupOrStep1MockTagline: "Uma API unificada para LLMs — uma chave, muitos modelos.",
  // setup page — OpenRouter step 2
  setupOrStep2Title: "Adicionar créditos",
  setupOrStep2BodyPrefix: "Navegue até ",
  setupOrStep2BodyLink: "Settings → Credits",
  setupOrStep2BodySuffix:
    ". Adicione pelo menos $20. Os modelos de código aberto baratos custam ~$0,25 por revisão; modelos de ponta como o Claude Opus ou o GPT-5 podem chegar a $5–$10 num artigo longo. A estimativa de custo mostrada antes da submissão é uma aproximação, não um teto. Deixe margem ou a revisão pode esgotar a chave a meio e falhar. Os créditos não utilizados não expiram.",
  setupOrStep2Annotation: "página de créditos",
  setupOrStep2MockSettings: "Settings → Credits",
  setupOrStep2MockAmount: "Montante",
  setupOrStep2MockButton: "Add credits",
  setupOrStep2MockBalance: "Saldo: $0,00",
  // setup page — OpenRouter step 3
  setupOrStep3Title: "Criar uma chave de API",
  setupOrStep3BodyPrefix: "Vá a ",
  setupOrStep3BodyLink: "Settings → Keys",
  setupOrStep3BodyMid: ", clique em “Create Key” e dê-lhe o nome ",
  setupOrStep3BodySuffix: ".",
  setupOrStep3Provisioning:
    "Certifique-se de que é uma chave de API normal — não uma chave de aprovisionamento/gestão da secção de integrações. As chaves de aprovisionamento podem criar e listar outras chaves, mas não podem executar inferência, e o coarse irá falhar com “User not found” se colar uma.",
  setupOrStep3CopyWarning: "Copie a chave agora — não a verá novamente.",
  setupOrStep3Annotation: "página de chaves",
  setupOrStep3MockSettings: "Settings → Keys",
  setupOrStep3MockButton: "Create Key",
  setupOrStep3MockKeyName: "Nome da chave",
  setupOrStep3MockYourKey: "A sua chave",
  // setup page — OpenRouter step 4
  setupOrStep4Title: "Definir um limite de gastos na chave",
  setupOrStep4BodyPrefix: "Na ",
  setupOrStep4BodyLink: "página de chaves",
  setupOrStep4BodyMid1: ", clique no menu ",
  setupOrStep4BodyMid2: " junto à sua nova chave, escolha “Edit” e defina o limite de crédito para ",
  setupOrStep4BodyAtLeast: "pelo menos $20",
  setupOrStep4BodySuffix:
    ". A chave deixa de funcionar assim que o limite é atingido, por isso cobranças-surpresa são impossíveis. Mas se o definir demasiado apertado, uma única revisão dispendiosa pode esgotá-lo a meio da execução.",
  setupOrStep4Annotation: "menu da chave",
  setupOrStep4MockEdit: "Edit",
  setupOrStep4MockLimitLabel: "Limite de crédito para esta chave",
  setupOrStep4MockButton: "Save",
  setupOrStep4WhyLabel: "Porque é que isto importa:",
  setupOrStep4WhyMid1: " o coarse é de código aberto — pode ",
  setupOrStep4WhyLink: "ler cada linha de código",
  setupOrStep4WhySuffix:
    ". A sua chave é enviada diretamente para o OpenRouter para executar a revisão e depois descartada — nunca é armazenada. Mas não tem de confiar em nós: o limite por chave garante que nunca pode gastar mais do que permite, mesmo no pior cenário.",
  setupOrStep4CostLabel: "Uma nota sobre estimativas de custo:",
  setupOrStep4CostBody:
    " a estimativa mostrada antes da submissão é uma heurística com uma margem de ~15%, não um teto rígido. O custo real em modelos de ponta com artigos longos pode chegar a ~2× a estimativa quando a verificação de provas e as reescritas de crítica entram em ação. Se o limite por chave ficar mesmo no valor da estimativa, uma revisão difícil pode esgotá-lo e falhar a meio. Deixe sempre margem.",
  // setup page — OpenRouter step 5
  setupOrStep5Title: "Colar no coarse",
  setupOrStep5Body: "Volte aqui, cole a sua chave no formulário e carregue o seu PDF.",
  setupOrStep5Annotation: "formulário do coarse",
  setupOrStep5MockEmail: "E-mail",
  setupOrStep5MockKey: "Chave OpenRouter",
  setupOrStep5MockButton: "Rever o meu artigo",
  // setup page — shared footer CTA
  setupReadyCta: "Pronto? Reveja o seu artigo →",
  // setup page — subscription tab intro
  setupSubHeading: "Usar a subscrição do seu agente de programação",
  setupSubIntro1:
    "Para utilizadores que já pagam por Claude Code, Codex ou Gemini CLI. A revisão é executada na sua subscrição e é cobrada aí. Paga apenas ~$0,15 ao OpenRouter pelo passo de OCR.",
  setupSubIntro2:
    "É executado localmente na sua máquina usando a sua própria conta de Claude Code, Codex ou Gemini CLI. O coarse.ink não recebe nem armazena o seu início de sessão do fornecedor. Aplicam-se na mesma os termos e limites de utilização do seu fornecedor. O coarse.ink não está associado à Anthropic, OpenAI ou Google.",
  // setup page — subscription step 1
  setupSubStep1Title: "Instalar um agente de programação",
  setupSubStep1Body:
    "Escolha aquele pelo qual paga. O Gemini CLI tem um nível gratuito se não pagar por nenhum. Instale-o a partir da página do próprio fornecedor — a documentação deles mantém-se atualizada.",
  setupSubStep1ClaudePrice: "Anthropic Pro ou Max",
  setupSubStep1CodexPrice: "ChatGPT Plus, Pro ou Business",
  setupSubStep1GeminiPrice: "O nível gratuito serve para a maioria dos artigos",
  setupSubStep1InstallLabel: "Instruções de instalação ↗",
  setupSubStep1Verify:
    "Execute o comando de teste para verificar a instalação + início de sessão. Se imprimir uma resposta, está tudo pronto.",
  setupSubStep1CardLogin: "início de sessão: ",
  setupSubStep1CardTest: "teste: ",
  // setup page — subscription step 2
  setupSubStep2Title: "Coloque uma chave OpenRouter na sua máquina (apenas PDFs)",
  setupSubStep2BodyPrefix:
    "Este passo só se aplica a artigos em PDF — as fontes que não são PDF (.tex, .md, .docx, …) são extraídas localmente sem OCR, por isso não precisam de chave OpenRouter em lado nenhum e pode saltar diretamente para o passo 3. Para PDFs, o coarse ainda precisa do OpenRouter para o passo de OCR (~$0,10 por artigo). Siga o separador ",
  setupSubStep2BodyTab: "Chave OpenRouter",
  setupSubStep2BodySuffix:
    " para criar uma conta, adicionar $1 de crédito e definir um limite de $2 por chave. A margem de $20 do caminho só com OpenRouter não é necessária aqui porque a própria revisão é executada na subscrição do seu agente de programação.",
  setupSubStep2KeyPrefix: "Depois coloque a chave na sua própria máquina: execute ",
  setupSubStep2KeyMid1: ", coloque-a num ",
  setupSubStep2KeyMid2: ", ou guarde-a em ",
  setupSubStep2KeySuffix:
    ". A sua CLI lê-a localmente quando executa a extração; o coarse.ink nunca a vê.",
  // setup page — subscription step 3
  setupSubStep3Title: "Carregue o seu artigo e escolha uma CLI",
  setupSubStep3BodyPrefix: "Na ",
  setupSubStep3BodyLink: "página principal",
  setupSubStep3BodyMid: ", largue o seu artigo (PDF, .tex, .md, .docx, …) no formulário e depois clique no menu ",
  setupSubStep3BodyButton: "Rever com a minha subscrição ▾",
  setupSubStep3BodySuffix:
    " e escolha a sua CLI. O coarse carrega o ficheiro, cria um token de entrega e mostra o prompt que irá colar no passo seguinte. Não cola a sua chave OpenRouter no formulário aqui; a CLI lê-a a partir da sua máquina (passo 2).",
  // setup page — subscription step 4
  setupSubStep4Title: "Cole o prompt na sua CLI",
  setupSubStep4BodyPrefix: "O coarse dá-lhe um único prompt em linguagem natural. Copie-o do painel, cole-o na sua sessão de ",
  setupSubStep4BodyMid1: ", ",
  setupSubStep4BodyMid2: ", ou ",
  setupSubStep4BodyMid3: " e carregue em enviar. O agente atualiza o seu pacote de skills, executa todo o pipeline do coarse nas suas próprias chamadas de subprocesso e imprime um URL ",
  setupSubStep4BodySuffix:
    " quando terminar. 10–25 minutos. Clique no URL para abrir a revisão concluída no coarse.ink.",
  setupSubStep4TimeoutLabel: "Se estiver a colar num agente de programação",
  setupSubStep4TimeoutSuffix:
    " (e não num terminal simples), aumente o tempo limite da ferramenta bash para pelo menos 45 min antes de enviar o prompt. Os tempos limite predefinidos dos agentes podem ser tão baixos como 2 min, muito abaixo do tempo de execução de revisão de 10–25 min.",
  // setup page — subscription step 5 (troubleshooting)
  setupSubStep5Title: "Se algo correr mal",
  setupSubTrouble1Symptom: "O botão “Tentar abrir o Claude Code / Codex” não faz nada.",
  setupSubTrouble1Fix:
    "O botão só funciona se tiver a aplicação de desktop instalada. Com uma instalação só de CLI, o navegador não consegue iniciar um terminal por si. Copie o prompt do painel e cole-o manualmente na sua CLI.",
  setupSubTrouble2Symptom: "“No such command ‘install-skills’” durante a execução do agente.",
  setupSubTrouble2FixPrefix: "Pode ignorar com segurança. O pacote de skills continua a carregar diretamente através de ",
  setupSubTrouble2FixSuffix: "; o agente irá continuar para o passo de revisão.",
  setupSubTrouble3Symptom: "A minha fatura da Anthropic / OpenAI / Google subiu após uma revisão.",
  setupSubTrouble3FixPrefix: "Verifique se existe ",
  setupSubTrouble3FixMid1: ", ",
  setupSubTrouble3FixMid2: ", ou ",
  setupSubTrouble3FixSuffix:
    " no ambiente da sua shell. Se estiver definido, a CLI anfitriã cobra à conta da API em vez da sua subscrição. A v1.3.0+ remove-os automaticamente, mas versões mais antigas não o faziam.",
  setupSubTrouble4Symptom: "Menos comentários do que o habitual (~10 em vez de 15–25).",
  setupSubTrouble4FixPrefix: "Uma secção atingiu o tempo limite de 30 min e foi descartada. Raro no esforço predefinido, mais comum com ",
  setupSubTrouble4FixSuffix:
    " em artigos longos. Volte a executar; baixe o esforço um nível se acontecer duas vezes.",

  // compare page (ComparePage.tsx)
  comparePanelErrorBody: "Não foi possível renderizar este. Experimente outro modelo ou comparação.",
  comparePaperCorticalCircuits: "Circuitos Corticais",
  comparePaperCosetCodes: "Códigos de Coset",
  comparePaperPopulationGenetics: "Genética de Populações",
  comparePaperTargetingInterventions: "Direcionamento de Intervenções",
  compareScoresShow: "Mostrar",
  compareScoresHide: "Ocultar",
  compareScoresToggleSuffix: " todas as pontuações entre artigos ",
  compareScoresColPaper: "Artigo",
  compareScoresColReference: "Referência",
  compareScoresColGpt5Mini: "GPT-5 Mini",
  compareScoresColGpt54: "GPT-5.4",
  compareScoresColSonnet: "Sonnet 4.6",
  compareScoresColKimi: "Kimi K2.5",
  compareScoresFootnote:
    "Avaliado pelo Gemini 3.1 Pro com entrada multimodal de PDF. 5,0/5 = corresponde à qualidade da referência. 5,5+/5 = supera-a.",
  compareJudgeShow: "Mostrar",
  compareJudgeHide: "Ocultar",
  compareJudgeToggleSuffix: " o prompt de juiz enviado ao Gemini 3.1 Pro ",
  compareJudgeExplain:
    "Para mitigar enviesamentos conhecidos de LLM-como-juiz, o juiz é executado duas vezes por avaliação com as duas revisões trocadas na ordem de apresentação, e as pontuações são calculadas em média entre ambas as ordens. Isto contraria o enviesamento posicional, em que os juízes favorecem sistematicamente a revisão que aparece primeiro. O prompt inclui também instruções específicas para contrariar o enviesamento de verbosidade (não recompensar a extensão em detrimento da substância), o enviesamento de confiança (não recompensar linguagem assertiva em detrimento de uma cautela correta), o enviesamento de autoridade (não recompensar o jargão ou o número de citações em detrimento da exatidão) e o enviesamento de leniência (usar toda a gama de pontuação de 1 a 6 em vez de se concentrar no meio). As revisões são rotuladas neutralmente como \"Review A\" e \"Review B\" em vez de \"referência\" e \"gerada\" para evitar pontuação baseada na proveniência.",
  compareJudgeSystemPromptLabel: "Prompt de sistema",
  compareJudgeUserPromptLabel: "Prompt de utilizador (artigo + revisões injetados em tempo de execução)",
  compareVsMid: " vs ",
  compareScoreOutOf: "/5",
  compareMetricCoverage: "Cobertura",
  compareMetricSpecificity: "Especificidade",
  compareMetricDepth: "Profundidade",
  compareJumpTo: "Saltar para",
  compareSectionOverallFeedback: "Comentários Gerais",
  compareSectionDetailedComments: "Comentários Detalhados",
  compareVisitPrefix: "Visitar ",
  comparePdfReviewSuffix: " revisão",
  comparePdfFallback: "Transfira o PDF se o iframe não renderizar ↓",
};
