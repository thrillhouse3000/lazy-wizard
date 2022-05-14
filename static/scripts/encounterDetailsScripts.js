let encounterId = $('#encounter-id').data('id')

async function loadMonsters() {
    let resp = await axios.post(`/encounter/${encounterId}`)
    let monsters = resp.data
    monsterTracker = {...monsters}

    appendMonsters(monsters)
}

$(document).ready(function(){
    loadMonsters()
})

async function updateEncounter() {
    let data = {
        id: encounterId,
        monsters: monsterTracker
        }  

    await axios.post(`/encounter/${encounterId}/update`, data)
}

$('#update-form').on('submit', updateEncounter)