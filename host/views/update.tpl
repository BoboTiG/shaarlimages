% this_site = site.copy()
% this_site["title"] += " • MàJ"
%include("header", site=this_site)

<div class="update">
    <table>
        <tr>
            <th class="num">N°</th>
            <th>Lien</th>
            <th class="maj">MàJ</th>
            <th class="nouveautes">Nouveautés</th>
        </tr>
        <tr class="tous">
            <td class="num">#</td>
            <td>Tous les shaarlis</td>
            <td class="maj"><a href="#" onClick="makeAllRequests(); return false;" title="Mettre à jour tous les shaarlis."></a></td>
            <td class="nouveautes" id="sum">0</td>
        </tr>
        %for idx, feed in enumerate(feeds):
        <tr class="{{ idx }}">
            <td class="num">{{ idx + 1 }}</td>
            <td>{{ feed }}</td>
            <td class="maj">
                <a href="" onClick="makeRequest({{ idx }}); return false;" title="Mettre à jour ce shaarli."></a>
            </td>
            <td class="nouveautes" id="feed-{{ idx }}"></td>
        </tr>
        %end
    </table>
</div>

<script src="/assets/js/update.js?v={{ version }}"></script>

%include("footer")
