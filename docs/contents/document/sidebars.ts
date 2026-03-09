import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Sidebar for the Docs section
 */
const sidebars: SidebarsConfig = {
  docs: [
    {
      type: 'doc',
      id: 'introduction',
      label: '📖 Introduction',
    },
    // {
    //   type: 'doc',
    //   id: 'getting-started-summary',
    //   label: '🚀 Getting Started Summary',
    // },
    {
      type: 'category',
      label: '🤟 Getting Started',
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'quick-start/quick-start',
          label: '⚡ Quick Start',
        },
        {
          type: 'doc',
          id: 'quick-start/requirements',
          label: '📋 Requirements',
        },
        {
          type: 'doc',
          id: 'quick-start/installation',
          label: '💾 Installation',
        },
        {
          type: 'doc',
          id: 'quick-start/how-to-run',
          label: '▶️ How to Run',
        },
      ],
    },
    // {
    //   type: 'doc',
    //   id: 'architecture',
    //   label: '🏗️ Architecture Overview',
    // },
    // {
    //   type: 'doc',
    //   id: 'usage-guide',
    //   label: '📖 Usage Guide',
    // },
    // {
    //   type: 'doc',
    //   id: 'examples',
    //   label: '💡 Examples & Tutorials',
    // },
    // {
    //   type: 'doc',
    //   id: 'deployment',
    //   label: '🚀 Deployment Guide',
    // },
    // {
    //   type: 'doc',
    //   id: 'best-practices',
    //   label: '✨ Best Practices',
    // },
    // {
    //   type: 'doc',
    //   id: 'documentation-overview',
    //   label: '📚 Documentation Overview',
    // },
    {
      type: 'category',
      label: '🧑‍💻 API References',
      items: [
        {
          type: 'doc',
          id: 'api-references/api-references',
          label: '📚 API References',
        },
      ],
    },
    {
      type: 'category',
      label: '👋 Contributing',
      items: [
        {
          type: 'doc',
          id: 'contribute/contribute',
          label: '🤝 Contribute',
        },
        {
          type: 'doc',
          id: 'contribute/report-bug',
          label: '🐛 Report Bug',
        },
        {
          type: 'doc',
          id: 'contribute/request-changes',
          label: '💡 Request Changes',
        },
        {
          type: 'doc',
          id: 'contribute/discuss',
          label: '💬 Discuss',
        },
      ],
    },
    {
      type: 'doc',
      id: 'changelog',
      label: '📝 Changelog',
    },
  ],
};

export default sidebars;
