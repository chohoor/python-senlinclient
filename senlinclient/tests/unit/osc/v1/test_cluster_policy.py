# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock


from senlinclient.osc.v1 import cluster_policy as osc_cluster_policy
from senlinclient.tests.unit.osc.v1 import fakes


class TestClusterPolicy(fakes.TestClusteringv1):
    def setUp(self):
        super(TestClusterPolicy, self).setUp()
        self.mock_client = self.app.client_manager.clustering


class TestClusterPolicyList(TestClusterPolicy):
    columns = ['policy_id', 'policy_name', 'policy_type', 'enabled']
    response = {"cluster_policies": [
        {
            "cluster_id": "7d85f602-a948-4a30-afd4-e84f47471c15",
            "cluster_name": "my_cluster",
            "enabled": True,
            "id": "06be3a1f-b238-4a96-a737-ceec5714087e",
            "policy_id": "714fe676-a08f-4196-b7af-61d52eeded15",
            "policy_name": "my_policy",
            "policy_type": "senlin.policy.deletion-1.0"
        },
        {
            "cluster_id": "7d85f602-a948-4a30-afd4-e84f47471c15",
            "cluster_name": "my_cluster",
            "enabled": True,
            "id": "abddc45e-ac31-4f90-93cc-db55a7d8dd6d",
            "policy_id": "e026e09f-a3e9-4dad-a1b9-d7ba316026a1",
            "policy_name": "my_policy",
            "policy_type": "senlin.policy.scaling-1.0"
        }
    ]}

    args = {
        'sort': 'name:asc',
    }

    def setUp(self):
        super(TestClusterPolicyList, self).setUp()
        self.cmd = osc_cluster_policy.ClusterPolicyList(self.app, None)
        cluster = mock.Mock()
        cluster.id = 'C1'
        self.mock_client.get_cluster = mock.Mock(
            return_value=cluster
        )
        self.mock_client.cluster_policies = mock.Mock(
            return_value=self.response)

    def test_cluster_policy_list(self):
        arglist = ['--sort', 'name:asc', '--filter', 'name=my_policy',
                   'my_cluster', '--full-id']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)
        self.mock_client.get_cluster.assert_called_with('my_cluster')
        self.mock_client.cluster_policies.assert_called_with(
            'C1',
            name='my_policy',
            **self.args)
        self.assertEqual(self.columns, columns)