(() => {
  const menuToggle = document.querySelector('.menu-toggle');
  const siteNav = document.querySelector('#site-nav');

  if (menuToggle && siteNav) {
    menuToggle.addEventListener('click', () => {
      const isOpen = siteNav.classList.toggle('is-open');
      menuToggle.setAttribute('aria-expanded', String(isOpen));
    });

    siteNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        siteNav.classList.remove('is-open');
        menuToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  const roleDetails = {
    scientist: {
      kicker: 'SCIENTIST / ONE TRAJECTORY',
      title: 'Fresh reasoning is a feature, not a reset button.',
      body: 'The Scientist decides what scientific question matters, how to implement the experiment, and whether to continue or pivot. Its context is local; its evidence returns to the world.',
      mark: '01',
    },
    meta: {
      kicker: 'META / ACROSS TRAJECTORIES',
      title: 'Persistence needs a curator, not a bigger transcript.',
      body: 'META audits reports against actual artifacts, scopes what the evidence supports, maintains shared research memory, and crystallizes strong implementations into a recoverable State.',
      mark: '02',
    },
    runtime: {
      kicker: 'RUNTIME / SYSTEM LIFETIME',
      title: 'Deterministic mechanics keep autonomy reviewable.',
      body: 'Runtime owns process isolation, cancellation, runner configuration, provenance, artifact capture, and State operations. It supports execution without becoming a third scientific voice.',
      mark: '03',
    },
  };

  const roleButtons = [...document.querySelectorAll('[data-role-button]')];
  const roleDetail = document.querySelector('#role-detail');
  const roleKicker = roleDetail?.querySelector('.role-detail-kicker');
  const roleTitle = roleDetail?.querySelector('h3');
  const roleBody = roleDetail?.querySelector('p');
  const roleMark = document.querySelector('.role-detail-mark');

  const updateRole = (role) => {
    const detail = roleDetails[role];
    if (!detail || !roleDetail) return;
    roleButtons.forEach((button) => {
      const isActive = button.dataset.roleButton === role;
      button.classList.toggle('is-active', isActive);
      button.setAttribute('aria-selected', String(isActive));
    });
    roleKicker.textContent = detail.kicker;
    roleTitle.textContent = detail.title;
    roleBody.textContent = detail.body;
    roleMark.textContent = detail.mark;
  };

  roleButtons.forEach((button) => {
    button.addEventListener('click', () => updateRole(button.dataset.roleButton));
  });

  const cycles = {
    1: {
      id: 'CYCLE 01 / E001–E003',
      model: 'gpt-5.6-sol',
      modelClass: 'model-dot-sol',
      description: 'The first Scientist read the task contract, tested leakage-safe historical encodings, and built a richer Factorization Machine. E003 reached a valid Full primary of 0.6016310, creating the first recoverable State.',
      title: 'Establish a valid starting point.',
      output: '15-field FM',
      result: 'Full primary 0.6016310',
    },
    2: {
      id: 'CYCLE 02 / E004–E007',
      model: 'gemini-3.7-flash',
      modelClass: 'model-dot-gemini',
      description: 'A fresh Scientist tested whether target encodings complemented the rich FM, then widened the representation. The 38-field FM became the stronger ensemble baseline while weaker architectures and feature families were recorded as negative evidence.',
      title: 'Make the representation richer.',
      output: '38-field FM',
      result: 'Screen-selected representation',
    },
    3: {
      id: 'CYCLE 03 / E008–E012',
      model: 'gpt-5.6-luna',
      modelClass: 'model-dot-luna',
      description: 'The next handoff focused on robustness and variance: multi-seed ensembling, wider representations, dense preference features, and field weighting were compared under the public-validation protocol.',
      title: 'Turn a promising line into a frontier.',
      output: '46-field FM + FwFM',
      result: 'Full primary 0.6054846',
    },
    4: {
      id: 'CYCLE 04 / E013',
      model: 'gemini-3.7-flash',
      modelClass: 'model-dot-gemini',
      description: 'The final Scientist inherited the evidence and tested the strongest remaining candidate: an eight-seed, 46-field Factorization Machine ensemble. E013 reached the retained public-validation primary of 0.6059363 and completed convergence 3/3.',
      title: 'Retain the strongest valid State.',
      output: '8-seed 46-field FM',
      result: 'Full primary 0.6059363',
    },
  };

  const cycleButtons = [...document.querySelectorAll('[data-cycle-button]')];
  const cycleDetail = document.querySelector('#cycle-detail');
  const cycleId = cycleDetail?.querySelector('.cycle-id');
  const cycleModel = cycleDetail?.querySelector('.cycle-model');
  const cycleDescription = cycleDetail?.querySelector('.cycle-detail-grid p');
  const cycleTitle = cycleDetail?.querySelector('.cycle-detail-grid h3');
  const cycleOutput = cycleDetail?.querySelector('.cycle-result strong');
  const cycleResult = cycleDetail?.querySelector('.cycle-result small');
  const cycleProgress = document.querySelector('.cycle-progress span');

  const updateCycle = (cycleNumber) => {
    const cycle = cycles[cycleNumber];
    if (!cycle || !cycleDetail) return;
    cycleButtons.forEach((button) => {
      const isActive = button.dataset.cycleButton === String(cycleNumber);
      button.classList.toggle('is-active', isActive);
      button.setAttribute('aria-selected', String(isActive));
    });
    cycleId.textContent = cycle.id;
    cycleModel.innerHTML = '<i class="model-dot ' + cycle.modelClass + '"></i> Scientist: <b>' + cycle.model + '</b><em> · META: gemini-3.7-flash</em>';
    cycleTitle.textContent = cycle.title;
    cycleDescription.textContent = cycle.description;
    cycleOutput.textContent = cycle.output;
    cycleResult.textContent = cycle.result;
    cycleProgress.style.width = String(Number(cycleNumber) * 25) + '%';
  };

  cycleButtons.forEach((button) => {
    button.addEventListener('click', () => updateCycle(button.dataset.cycleButton));
  });
})();
