let encounterId = $('#encounter-id').data('id')

$(document).ready(function(){
    loadMonsters()
})

async function loadMonsters() {
    let resp = await axios.post(`/encounter/${encounterId}`)
    let monsters = resp.data
    await getMonsters(monsters)
    appendMonsters(monsterTracker)
}

async function getMonsters(monsters) {
    for (let i in monsters) {
        loadingSpinner('#monster-section')
        let resp = await axios.get(`https://api.open5e.com/monsters/?name=${i}`)
        endSpinner()
        let monster = resp.data.results[0]
        monsterTracker[`${monster.slug}`] = {}
        monsterTracker[`${monster.slug}`]['count'] = parseInt(monsters[i])
        monsterTracker[`${monster.slug}`]['name'] = monster.name
        monsterTracker[`${monster.slug}`]['data'] = monster
    }
}

function submitUpdate() {
    let monsterRef = getRef(monsterTracker)
    $('#monsterRef').val(monsterRef)
    $('#update-form').submit()
}

$('#update-btn').on('click', submitUpdate)