let encounterId = $('#encounter-id').data('id')

async function loadMonsters() {
    let resp = await axios.post(`/encounter/${encounterId}`)
    let monsters = resp.data
    await getMonsters(monsters)
    appendMonsters(monsterTracker)
}

async function getMonsters(monsters) {
    for (let i in monsters) {
        let resp = await axios.get(`https://api.open5e.com/monsters/?name=${i}`)
        let monster = resp.data.results[0]
        monsterTracker[`${monster.slug}`] = {}
        monsterTracker[`${monster.slug}`]['count'] = parseInt(monsters[i])
        monsterTracker[`${monster.slug}`]['name'] = monster.name
        monsterTracker[`${monster.slug}`]['data'] = monster
    }
}

$(document).ready(function(){
    loadMonsters()
})

// async function updateEncounter() {
//     let data = {
//         id: encounterId,
//         monsters: monsterTracker
//         }  

//     await axios.post(`/encounter/${encounterId}/update`, data)
// }

// $('#update-form').on('submit', updateEncounter)

function getRef(monsterTracker) {
    let monsterRef = {}
    for (let monster in monsterTracker) {
        monsterRef[monsterTracker[`${monster}`].name] = `${monsterTracker[monster].count}`
    }
    return JSON.stringify(monsterRef)
}

function submitUpdate() {
    let monsterRef = getRef(monsterTracker)
    $('#monsterRef').val(monsterRef)
    $('#update-form').submit()
}

$('#update-btn').on('click', submitUpdate)