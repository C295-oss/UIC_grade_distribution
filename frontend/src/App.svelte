<script>
    import Chart from 'chart.js/auto';

    let subject = "";
    let classNumber = "";
    let formLoading = false;

    let profRating = null;
    let gradeDistribution = null;

    // Keep track of chart instances
    let charts = [];

    async function getGradeDistribution() {
        try {
            let url = `http://127.0.0.1:8000/find_class/${subject}`;
            if (classNumber) {
                url += `/${classNumber}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            // Extract classes and professor_ratings from the response
            gradeDistribution = data.classes;
            profRating = data.professor_ratings;

            console.log("Grade Distribution Data:", gradeDistribution);
            console.log("Professor Ratings Data:", profRating);

            updateGraphs();
        } catch (error) {
            console.error("Error fetching grade distribution:", error);
            return null;
        }
    }

    function graph_grades(ctx, a_val, b_val, c_val, d_val, f_val) {
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['A', 'B', 'C', 'D', 'F'],
                datasets: [{
                    label: 'Grades Distribution',
                    data: [a_val, b_val, c_val, d_val, f_val],
                    backgroundColor: [
                        'rgba(34, 153, 84, 0.2)',
                        'rgba(46, 204, 113, 0.2)',
                        'rgba(244, 208, 63, 0.2)',
                        'rgba(220, 118, 51, 0.2)',
                        'rgba(231, 76, 60, 0.2)'
                    ],
                    borderColor: [
                        'rgba(34, 153, 84, 1)',
                        'rgba(46, 204, 113, 1)',
                        'rgba(244, 208, 63, 1)',
                        'rgba(220, 118, 51, 1)',
                        'rgba(231, 76, 60, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {}
        });
    }

    async function updateGraphs()
    {
        if (gradeDistribution && gradeDistribution.length > 0) {
            // Destroy any existing charts
            charts.forEach(chart => chart.destroy());
            charts = [];

            gradeDistribution.forEach((entry, index) => {
                const ctx = document.getElementById(`myChart${index}`);
                const chart = graph_grades(ctx, entry["A"], entry["B"], entry["C"], entry["D"], entry["F"]);
                charts.push(chart); 
            });
        }
    }
</script>

<!-- Nav bar and search -->
<div class="nav">
    <input
        class="search"
        bind:value={subject}
        type="text"
        placeholder="Course"
    />
    <input
        class="search"
        bind:value={classNumber}
        type="text"
        placeholder="Class Number"
    />
    <button on:click={getGradeDistribution} id="submit_search" type="submit">
        Search
    </button>
</div>

<!-- Body content -->
<div class="body">
    {#if formLoading}
        Loading...
    {/if}

    <!-- Grade distributions -->
    <div id="grade_dist">
        {#each gradeDistribution as entry, index}
            <div class="item">
                <p></p>
                <p>{entry["file_name"]} - {entry["CRS TITLE"]} ({entry["CRS SUBJ CD"]} {entry["CRS NBR"]})</p>
                <p>{entry["Primary Instructor"]}</p>

                <canvas id="myChart{index}" style="width:100%;max-width:700px"></canvas>
            </div>
        {:else}
            <p>No grade distributions yet.</p>
        {/each}
    </div>

    <!-- Professor ratings -->
    <div id="prof_rating">
        {#if profRating}
            <pre>
                <div class="prof_rating_box">
                    <h2><b>{profRating['name']} -- {profRating['avg_rating']}/5</b></h2>
                    <p>{profRating['prof_dept']}</p>
                    <p>{profRating['would_take_again']} students would take again</p>
                </div>
            </pre>
        {:else}
            <p>No professor rating data available</p>
        {/if}
    </div>
</div>
