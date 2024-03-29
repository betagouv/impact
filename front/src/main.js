import ExternalFieldToggle from './lib/ExternalFieldToggle.svelte'
import GroupeFields from './lib/GroupeFields.svelte'
import InteretPublicField from './lib/InteretPublicField.svelte'
import SimulationChange from './lib/SimulationChange.svelte'
import SearchEntreprise from './lib/SearchEntreprise.svelte'

for (let externalFieldToggle of document.getElementsByClassName("svelte-external-field-toggle")) {
  new ExternalFieldToggle({
    target: externalFieldToggle,
    props: {
      toggleId: externalFieldToggle.dataset.toggleId,
      fieldName: externalFieldToggle.dataset.fieldName,
      fieldContainerId: externalFieldToggle.dataset.fieldContainerId,
      externalFieldsInStepFieldId: externalFieldToggle.dataset.externalFieldsInStepFieldId
    }
  })
}

const searchEntrepriseElement = document.getElementById("svelte-search-entreprise")
if (searchEntrepriseElement) {
  new SearchEntreprise({
    target: searchEntrepriseElement,
    props: {
      siren: searchEntrepriseElement.dataset.siren,
      denomination: searchEntrepriseElement.dataset.denomination
    },
    hydrate: true,
  })
}

const appartientGroupeFieldElement = document.getElementById("svelte-appartient-groupe-field")
if (appartientGroupeFieldElement) {
  new GroupeFields({
    target: appartientGroupeFieldElement,
  })
}

const estInteretPublicFieldElement = document.getElementById("svelte-est-interet-public-field")
if (estInteretPublicFieldElement) {
  new InteretPublicField({
    target: estInteretPublicFieldElement,
  })
}


if (document.getElementById("svelte-simulation-result")) {
  new SimulationChange({
    target: document.getElementById("svelte-simulation-form")
  })
}
